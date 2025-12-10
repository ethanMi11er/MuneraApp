from django.contrib import messages
from django.db.models import Count, Q, F
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
import secrets
import string

from projects.models import Project, ProjectMember, Task, Status
from .models import Organization, OrganizationMember, Role
from users.models import User


def get_session_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


class MyOrganizationsView(View):
    template_name = 'organization/my_organizations.html'
    
    def get(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        
        memberships = OrganizationMember.objects.filter(user=user).select_related('organization')
        
        return render(request, self.template_name, {
            'user': user,
            'memberships': memberships
        })


class JoinOrganizationView(View):
    
    def get(self, request):
        return redirect('my_organizations')
    
    def post(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        
        org_code = request.POST.get('org_code', '').strip()
        
        if not org_code:
            messages.error(request, "Please enter an organization code.")
            return redirect('my_organizations')
        
        try:
            organization = Organization.objects.get(org_code=org_code)
        except Organization.DoesNotExist:
            messages.error(request, "Invalid organization code. Please check the code and try again.")
            return redirect('my_organizations')
        
        if OrganizationMember.objects.filter(organization=organization, user=user).exists():
            messages.warning(request, f"You are already a member of '{organization.org_name}'.")
            return redirect('my_organizations')
        
        OrganizationMember.objects.create(
            organization=organization,
            user=user,
            role=Role.Member
        )
        
        messages.success(request, f"You have successfully joined '{organization.org_name}'!")
        return redirect('my_organizations')


class LeaveOrganizationView(View):
    def post(self, request, org_id):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        
        organization = get_object_or_404(Organization, org_id=org_id)
        
        try:
            membership = OrganizationMember.objects.get(organization=organization, user=user)
        except OrganizationMember.DoesNotExist:
            messages.error(request, "You are not a member of this organization.")
            return redirect('my_organizations')
        
        if organization.org_creator == user:
            messages.error(request, "You cannot leave an organization you created. Consider transferring ownership or deleting the organization.")
            return redirect('my_organizations')
        
        membership.delete()
        messages.success(request, f"You have successfully left '{organization.org_name}'.")
        
        return redirect('my_organizations')
    
    def get(self, request, org_id):
        return redirect('my_organizations')


class CreateOrganizationView(View):
    template_name = 'organization/create_organization.html'
    
    def get(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        
        return render(request, self.template_name, {'user': user})
    
    def post(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        
        org_name = request.POST.get('org_name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not org_name:
            messages.error(request, "Organization name is required.")
            return render(request, self.template_name, {
                'user': user,
                'org_name': org_name,
                'description': description
            })
        
        if len(org_name) > 30:
            messages.error(request, "Organization name must be 30 characters or less.")
            return render(request, self.template_name, {
                'user': user,
                'org_name': org_name,
                'description': description
            })
        
        if description and len(description) > 500:
            messages.error(request, "Description must be 500 characters or less.")
            return render(request, self.template_name, {
                'user': user,
                'org_name': org_name,
                'description': description
            })
        
        org_code = self.generate_unique_org_code()
        
        try:
            organization = Organization.objects.create(
                org_creator=user,
                org_name=org_name,
                org_code=org_code,
                description=description if description else None
            )
        
            OrganizationMember.objects.create(
                organization=organization,
                user=user,
                role=Role.Manager
            )
            
            messages.success(request, f"Organization '{org_name}' has been created successfully! Organization code: {org_code}")
            return redirect('my_organizations')
            
        except Exception as e:
            messages.error(request, f"An error occurred while creating the organization: {str(e)}")
            return render(request, self.template_name, {
                'user': user,
                'org_name': org_name,
                'description': description
            })
    
    def generate_unique_org_code(self, length=8):
        characters = string.ascii_uppercase + string.digits
        while True:
            org_code = ''.join(secrets.choice(characters) for _ in range(length))
            if not Organization.objects.filter(org_code=org_code).exists():
                return org_code


class OrganizationDetailView(View):
    template_name = 'organization/organization_detail.html'

    def get(self, request, org_id):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        organization = get_object_or_404(
            Organization.objects.prefetch_related('memberships__user'),
            org_id=org_id,
            members=user
        )
        membership = OrganizationMember.objects.filter(organization=organization, user=user).first()
        projects = organization.projects.all().annotate(
            open_tasks=Count('tasks', filter=~Q(tasks__status=Status.Done))
        ).select_related('organization')
        manager_task_filter = Q(
            project__organization=organization,
            project__memberships__user=user,
            project__memberships__role=ProjectMember.Role.MANAGER.value,
        )
        my_tasks = Task.objects.filter(
            Q(project__organization=organization, assignments__user=user) | manager_task_filter
        ).select_related('project').distinct().order_by(F('due_date').asc(nulls_last=True))
        is_org_manager = membership and membership.role == Role.Manager

        context = {
            'user': user,
            'organization': organization,
            'membership': membership,
            'is_org_manager': is_org_manager,
            'projects': projects,
            'member_list': organization.memberships.select_related('user'),
            'my_tasks': my_tasks,
        }
        return render(request, self.template_name, context)


class OrganizationMemberRoleUpdateView(View):
    def post(self, request, org_id, user_id):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        organization = get_object_or_404(Organization, org_id=org_id)
        acting_membership = OrganizationMember.objects.filter(organization=organization, user=user).first()
        if not acting_membership or acting_membership.role != Role.Manager:
            messages.error(request, "Only organization managers can change member roles.")
            return redirect('organization_detail', org_id=org_id)

        if user.pk == user_id:
            messages.warning(request, "You cannot change your own role.")
            return redirect('organization_detail', org_id=org_id)

        membership = get_object_or_404(OrganizationMember, organization=organization, user_id=user_id)
        new_role = request.POST.get('role')
        if new_role not in Role.values:
            messages.error(request, "Invalid role selected.")
            return redirect('organization_detail', org_id=org_id)

        if membership.role == Role.Manager and new_role != Role.Manager:
            manager_count = OrganizationMember.objects.filter(organization=organization, role=Role.Manager).count()
            if manager_count <= 1:
                messages.error(request, "Each organization must have at least one manager.")
                return redirect('organization_detail', org_id=org_id)

        membership.role = new_role
        membership.save(update_fields=['role'])
        messages.success(request, f"{membership.user.user_name} is now a {new_role}.")
        return redirect('organization_detail', org_id=org_id)

    def get(self, request, org_id, user_id):
        return redirect('organization_detail', org_id=org_id)


class DeleteOrganizationView(View):
    def post(self, request, org_id):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        
        organization = get_object_or_404(Organization, org_id=org_id)

        try:
            membership = OrganizationMember.objects.get(organization=organization, user=user)
        except OrganizationMember.DoesNotExist:
            messages.error(request, "You are not a member of this organization.")
            return redirect('my_organizations')
        
        if membership.role != Role.Manager:
            messages.error(request, "You do not have permission to delete this organization. Only managers can delete organizations.")
            return redirect('my_organizations')
        
        org_name = organization.org_name
        
        organization.delete()
        messages.success(request, f"Organization '{org_name}' has been successfully deleted.")
        
        return redirect('my_organizations')
    
    def get(self, request, org_id):
        return redirect('my_organizations')
