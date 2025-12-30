from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from organization.models import OrganizationMember, Role as OrgRole
from users.models import User
from .forms import ProjectForm, TaskForm
from .models import Project, ProjectMember, Task


def get_authenticated_user(request):
    """Fetch the current user based on our session-based auth."""
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


class SessionUserMixin:
    current_user = None

    def dispatch(self, request, *args, **kwargs):
        self.current_user = get_authenticated_user(request)
        if not self.current_user:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get_membership(self, project):
        return ProjectMember.objects.filter(project=project, user=self.current_user).first()

    def is_manager(self, project):
        org_membership = self.get_org_membership(project.organization)
        return bool(org_membership and org_membership.role == OrgRole.Manager)

    def get_org_membership(self, organization):
        return OrganizationMember.objects.filter(organization=organization, user=self.current_user).first()

    def is_org_member(self, organization):
        return self.get_org_membership(organization) is not None


class TasksPageView(SessionUserMixin, View):
    template_name = 'projects/tasks.html'

    def get(self, request):
        assigned_tasks = Task.objects.filter(assignments__user=self.current_user)
        managed_tasks = Task.objects.filter(
            project__organization__memberships__user=self.current_user,
            project__organization__memberships__role=OrgRole.Manager,
        )
        tasks = (assigned_tasks | managed_tasks).select_related('project').distinct().order_by('due_date')
        manager_project_ids = set(Project.objects.filter(
            organization__memberships__user=self.current_user,
            organization__memberships__role=OrgRole.Manager
        ).values_list('project_id', flat=True))
        can_create_tasks = OrganizationMember.objects.filter(
            user=self.current_user,
            role=OrgRole.Manager,
        ).exists()
        context = {
            'tasks': tasks,
            'user': self.current_user,
            'manager_project_ids': manager_project_ids,
            'can_create_tasks': can_create_tasks,
        }
        return render(request, self.template_name, context)


class TaskDeleteView(SessionUserMixin, View):

    def post(self, request, task_id):
        task = get_object_or_404(Task, task_id=task_id)
        if not self.is_manager(task.project):
            messages.error(request, "Only project managers can delete tasks.")
            return redirect('projects:project-detail', project_id=task.project.project_id)

        task.delete()
        messages.success(request, "Task removed.")
        return redirect('projects:project-detail', project_id=task.project.project_id)

    def get(self, request, task_id):
        task = get_object_or_404(Task, task_id=task_id)
        messages.info(request, "Use the delete button to remove tasks.")
        return redirect('projects:project-detail', project_id=task.project.project_id)


class TaskAddView(SessionUserMixin, View):

    template_name = 'projects/add_task.html'

    def get(self, request):
        if not OrganizationMember.objects.filter(user=self.current_user, role=OrgRole.Manager).exists():
            messages.error(request, "Only organization managers can create tasks.")
            return redirect('my_organizations')
        form = TaskForm(user=self.current_user)
        if not form.fields['project'].queryset.exists():
            messages.error(request, "You must manage an organization with projects before adding tasks.")
            return redirect('my_organizations')
        return render(request, self.template_name, {'form': form, 'user': self.current_user})

    def post(self, request):
        if not OrganizationMember.objects.filter(user=self.current_user, role=OrgRole.Manager).exists():
            messages.error(request, "Only organization managers can create tasks.")
            return redirect('my_organizations')
        form = TaskForm(request.POST, user=self.current_user)
        if form.is_valid():
            task = form.save()
            messages.success(request, "Task created.")
            return redirect('projects:project-detail', project_id=task.project.project_id)
        return render(request, self.template_name, {'form': form, 'user': self.current_user})


class TaskDetailView(SessionUserMixin, View):
    template_name = 'projects/task_detail.html'

    def get(self, request, task_id):
        task = get_object_or_404(Task.objects.select_related('project__organization'), task_id=task_id)
        org_membership = self.get_org_membership(task.project.organization)
        if not org_membership:
            messages.error(request, "You must belong to this organization to view its tasks.")
            return redirect('my_organizations')

        can_edit = self.is_manager(task.project)
        form = TaskForm(instance=task, project=task.project, user=self.current_user)
        if not can_edit:
            for field in form.fields.values():
                field.disabled = True

        context = {
            'task': task,
            'project': task.project,
            'form': form,
            'can_edit': can_edit,
            'org_membership': org_membership,
            'user': self.current_user,
        }
        return render(request, self.template_name, context)

    def post(self, request, task_id):
        task = get_object_or_404(Task.objects.select_related('project__organization'), task_id=task_id)
        org_membership = self.get_org_membership(task.project.organization)
        if not org_membership:
            messages.error(request, "You must belong to this organization to modify its tasks.")
            return redirect('my_organizations')

        can_edit = self.is_manager(task.project)
        if not can_edit:
            messages.error(request, "Only managers can update this task.")
            return redirect('projects:task-detail', task_id=task_id)

        form = TaskForm(request.POST, instance=task, project=task.project, user=self.current_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Task updated.")
            return redirect('projects:task-detail', task_id=task_id)

        context = {
            'task': task,
            'project': task.project,
            'form': form,
            'can_edit': can_edit,
            'user': self.current_user,
        }
        return render(request, self.template_name, context)


class ProjectCreateView(SessionUserMixin, View):
    template_name = 'projects/create_project.html'

    def get(self, request):
        if not OrganizationMember.objects.filter(user=self.current_user, role=OrgRole.Manager).exists():
            messages.error(request, "Only organization managers can create projects.")
            return redirect('my_organizations')
        form = ProjectForm(user=self.current_user)
        return render(request, self.template_name, {'form': form, 'user': self.current_user})

    def post(self, request):
        if not OrganizationMember.objects.filter(user=self.current_user, role=OrgRole.Manager).exists():
            messages.error(request, "Only organization managers can create projects.")
            return redirect('my_organizations')

        form = ProjectForm(request.POST, user=self.current_user)
        if form.is_valid():
            project = form.save(commit=False)
            if not OrganizationMember.objects.filter(
                organization=project.organization,
                user=self.current_user,
                role=OrgRole.Manager,
            ).exists():
                messages.error(request, "You must be a manager of the organization to create projects there.")
                return redirect('my_organizations')
            project.created_by = self.current_user
            project.save()

            ProjectMember.objects.create(
                project=project,
                user=self.current_user,
                role=ProjectMember.Role.MANAGER.value
            )
            messages.success(request, "Project created.")
            return redirect('projects:project-detail', project_id=project.project_id)

        return render(request, self.template_name, {'form': form, 'user': self.current_user})


class MyProjectsView(SessionUserMixin, View):
    template_name = 'projects/my_projects.html'

    def get(self, request):
        user_projects = Project.objects.filter(
            organization__memberships__user=self.current_user
        ).select_related('organization').distinct()
        can_create_projects = OrganizationMember.objects.filter(
            user=self.current_user,
            role=OrgRole.Manager,
        ).exists()
        context = {
            'projects_list': user_projects,
            'user': self.current_user,
            'can_create_projects': can_create_projects,
        }
        return render(request, self.template_name, context)


class ProjectDetailView(SessionUserMixin, View):
    template_name = 'projects/project_detail.html'

    def get(self, request, project_id):
        project = get_object_or_404(Project.objects.select_related('organization'), project_id=project_id)
        org_membership = self.get_org_membership(project.organization)
        if not org_membership:
            messages.error(request, "You must belong to this organization to view its projects.")
            return redirect('my_organizations')

        membership = self.get_membership(project)
        user_role = membership.role if membership else None
        is_manager = self.is_manager(project)

        project_members = ProjectMember.objects.filter(project=project).select_related('user')
        tasks = Task.objects.filter(project=project).select_related('project')
        my_tasks = tasks.filter(assignments__user=self.current_user)

        context = {
            'project': project,
            'project_members': project_members,
            'all_tasks': tasks,
            'my_tasks': my_tasks,
            'user_role': user_role,
            'is_manager': is_manager,
            'org_membership': org_membership,
            'user': self.current_user,
        }
        return render(request, self.template_name, context)


class ProjectTaskCreateView(SessionUserMixin, View):
    template_name = 'projects/create_task.html'

    def get(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        if not self.is_manager(project):
            messages.error(request, "Only organization managers can create tasks for this project.")
            return redirect('projects:project-detail', project_id=project_id)

        form = TaskForm(project=project, user=self.current_user)
        return render(request, self.template_name, {'form': form, 'project': project, 'user': self.current_user})

    def post(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        if not self.is_manager(project):
            messages.error(request, "Only organization managers can create tasks for this project.")
            return redirect('projects:project-detail', project_id=project_id)

        form = TaskForm(request.POST, project=project, user=self.current_user)
        if form.is_valid():
            form.save()
            messages.success(request, "Task created and assigned.")
            return redirect('projects:project-detail', project_id=project.project_id)

        return render(request, self.template_name, {'form': form, 'project': project, 'user': self.current_user})


class ProjectMemberRemoveView(SessionUserMixin, View):
    def post(self, request, project_id, user_id):
        project = get_object_or_404(Project, project_id=project_id)

        if not self.is_manager(project):
            messages.error(request, "Only managers can remove members.")
            return redirect('projects:project-detail', project_id=project_id)

        if self.current_user.pk == user_id:
            messages.error(request, "You cannot remove yourself from the project.")
            return redirect('projects:project-detail', project_id=project_id)

        member_to_remove = get_object_or_404(ProjectMember, project=project, user_id=user_id)
        member_to_remove.delete()

        messages.success(request, "Member removed successfully.")
        return redirect('projects:project-detail', project_id=project_id)

    def get(self, request, project_id, user_id):
        messages.info(request, "Use the remove button to manage members.")
        return redirect('projects:project-detail', project_id=project_id)


class ProjectMemberAddView(SessionUserMixin, View):
    def post(self, request, project_id):
        project = get_object_or_404(Project, project_id=project_id)

        if not self.is_manager(project):
            messages.error(request, "You do not have permission to add members to this project.")
            return redirect('projects:project-detail', project_id=project_id)

        username_to_add = request.POST.get('username')

        try:
            user_to_add = User.objects.get(user_name=username_to_add)
        except User.DoesNotExist:
            messages.error(request, "User not found. Please check the username.")
            return redirect('projects:project-detail', project_id=project_id)

        if ProjectMember.objects.filter(project=project, user=user_to_add).exists():
            messages.warning(request, f"{user_to_add.user_name} is already a member of this project.")
            return redirect('projects:project-detail', project_id=project_id)

        if not OrganizationMember.objects.filter(organization=project.organization, user=user_to_add).exists():
            messages.error(request, "Add this user to the organization before assigning them to the project.")
            return redirect('projects:project-detail', project_id=project_id)

        ProjectMember.objects.create(
            project=project,
            user=user_to_add,
            role=ProjectMember.Role.MEMBER.value
        )
        messages.success(request, f"{user_to_add.user_name} was added to the project!")
        return redirect('projects:project-detail', project_id=project_id)

    def get(self, request, project_id):
        return redirect('projects:project-detail', project_id=project_id)
