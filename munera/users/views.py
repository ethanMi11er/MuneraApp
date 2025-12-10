from datetime import date

from django.contrib import messages
from django.db.models import Count, Q, F
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views import View
from organization.models import Organization, OrganizationMember, Role as OrgRole
from projects.models import Project, ProjectMember, Task, Status
from users.forms import UserProfileForm
from users.models import User
from users.serializers import LoginSerializer, UserCreateSerializer


def get_session_user(request):
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    try:
        return User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return None


class Login(View):
    def get(self, request):
        return render(request, 'login.html', {"form_data": {}})

    def post(self, request):
        serializer = LoginSerializer(data=request.POST)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            user.last_login = timezone.now()
            user.save(update_fields=["last_login"])
            request.session["user_id"] = user.pk
            messages.success(request, "Welcome back!")
            return redirect('home')

        form_data = {
            'username': request.POST.get('username', ''),
        }
        messages.error(request, "Invalid username or password.")
        return render(request, 'login.html', {"form_data": form_data})


class Logout(View):
    def get(self, request):
        request.session.pop('user_id', None)
        messages.info(request, "You have been logged out.")
        return redirect('login')


class Create_Account(View):
    template_name = 'create_account.html'

    def get(self, request):
        return render(request, self.template_name, {"form_data": {}})

    def post(self, request):
        serializer = UserCreateSerializer(data=request.POST)
        if serializer.is_valid():
            serializer.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')

        form_data = {
            'username': request.POST.get('username', ''),
            'email': request.POST.get('email', ''),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'alias': request.POST.get('alias', ''),
        }
        messages.error(request, "Please correct the errors below.")
        try:
            errors = serializer.errors
            if isinstance(errors, dict):
                for _, errs in errors.items():
                    if isinstance(errs, (list, tuple)):
                        for e in errs:
                            messages.error(request, str(e))
                    else:
                        messages.error(request, str(errs))
            else:
                messages.error(request, str(errors))
        except Exception:
            pass

        return render(request, self.template_name, {"form_data": form_data})


class Home(View):
    template_name = 'home.html'

    def get(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        today = date.today()

        memberships = OrganizationMember.objects.filter(user=user).select_related('organization')
        organizations = Organization.objects.filter(members=user).select_related('org_creator')
        projects_qs = Project.objects.filter(members=user).select_related('organization')
        projects = projects_qs.annotate(
            open_tasks=Count('tasks', filter=~Q(tasks__status=Status.Done))
        )
        manager_task_filter = Q(
            project__memberships__user=user,
            project__memberships__role=ProjectMember.Role.MANAGER.value,
        )
        user_tasks = Task.objects.filter(
            Q(assignments__user=user) | manager_task_filter
        ).select_related('project').distinct()
        open_tasks = user_tasks.exclude(status=Status.Done)
        focus_task = open_tasks.exclude(due_date__isnull=True).order_by('due_date').first() or open_tasks.first()
        open_tasks_ordered = open_tasks.order_by(F('due_date').asc(nulls_last=True))
        can_create_projects = OrganizationMember.objects.filter(user=user, role=OrgRole.Manager).exists()

        context = {
            "user": user,
            "organizations": organizations,
            "memberships": memberships,
            "projects": projects,
            "organization_count": memberships.count(),
            "project_count": projects_qs.count(),
            "open_tasks_count": open_tasks.count(),
            "due_today_count": open_tasks.filter(due_date=today).count(),
            "open_tasks": open_tasks_ordered[:8],
            "upcoming_tasks": open_tasks.filter(due_date__gte=today).order_by('due_date')[:5],
            "recent_projects": projects_qs.order_by('-start_date', '-project_id')[:4],
            "focus_task": focus_task,
            "can_create_projects": can_create_projects,
            "can_create_tasks": can_create_projects,
        }
        return render(request, self.template_name, context)


class Profile(View):
    template_name = 'profile.html'

    def get(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')
        return render(request, self.template_name, {"user": user})


class EditProfile(View):
    template_name = 'edit_profile.html'

    def get(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        form = UserProfileForm(instance=user)
        context = {
            "user": user,
            'form': form,
        }
        return render(request, self.template_name, context)

    def post(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect('profile')

        messages.error(request, "Please correct the errors below.")
        context = {
            "user": user,
            'form': form,
        }
        return render(request, self.template_name, context)


class ChangePassword(View):
    template_name = 'change_password.html'

    def get(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        context = {"user": user}
        return render(request, self.template_name, context)

    def post(self, request):
        user = get_session_user(request)
        if not user:
            return redirect('login')

        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return render(request, self.template_name, {"user": user})

        if current_password == new_password:
            messages.error(request, "New password cannot be the same as your current password.")
            return render(request, self.template_name, {"user": user})

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return render(request, self.template_name, {"user": user})

        if len(new_password) < 8:
            messages.error(request, "New password must be at least 8 characters long.")
            return render(request, self.template_name, {"user": user})

        user.set_password(new_password)
        user.save()
        messages.success(request, "Password changed successfully.")
        return redirect('profile')
