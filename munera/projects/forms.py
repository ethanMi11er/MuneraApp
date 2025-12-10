from django import forms
from .models import Project, Task, TaskAssignment
from organization.models import Organization, OrganizationMember, Role as OrgRole
from users.models import User

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'project_desc', 'start_date', 'end_date', 'organization']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['organization'].queryset = Organization.objects.filter(
                memberships__user=user,
                memberships__role=OrgRole.Manager,
            ).distinct()
        else:
            self.fields['organization'].queryset = Organization.objects.all()
        
class TaskForm(forms.ModelForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=User.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Task
        fields = ['project', 'task_name', 'task_desc', 'status', 'due_date', 'assignees']
        widgets = {
            'project': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self._user = user

        if user:
            self.fields['project'].queryset = Project.objects.filter(
                organization__memberships__user=user,
                organization__memberships__role=OrgRole.Manager,
            ).distinct()
        else:
            self.fields['project'].queryset = Project.objects.all()

        self._project_context = None
        if project:
            self._project_context = project
            self.fields['project'].initial = project
            self.fields['project'].queryset = Project.objects.filter(pk=project.pk)
            self.fields['project'].widget = forms.HiddenInput()
        else:
            selected_project_id = self.data.get('project') or self.initial.get('project')
            if selected_project_id:
                try:
                    self._project_context = Project.objects.get(pk=selected_project_id)
                except (Project.DoesNotExist, ValueError, TypeError):
                    self._project_context = None

        if self._project_context:
            self.fields['assignees'].queryset = User.objects.filter(
                project_memberships__project=self._project_context
            )
        elif user:
            self.fields['assignees'].queryset = User.objects.filter(
                project_memberships__project__in=self.fields['project'].queryset
            ).distinct()

        if self.instance.pk and not self.fields['assignees'].initial:
            self.fields['assignees'].initial = list(
                self.instance.assignees.values_list('pk', flat=True)
            )

    def clean_project(self):
        project = self.cleaned_data.get('project') or self._project_context
        if not project:
            raise forms.ValidationError("Please choose a project.")

        if self._user:
            is_org_manager = OrganizationMember.objects.filter(
                organization=project.organization,
                user=self._user,
                role=OrgRole.Manager,
            ).exists()
            if not is_org_manager:
                raise forms.ValidationError("Only organization managers can create or update tasks.")
        return project

    def clean_assignees(self):
        assignees = self.cleaned_data.get('assignees')
        project = self._project_context or self.cleaned_data.get('project')
        if project and assignees:
            not_members = assignees.exclude(project_memberships__project=project)
            if not_members.exists():
                raise forms.ValidationError("All assignees must be members of this project.")
        return assignees

    def save(self, commit=True):
        task = super().save(commit=False)
        project = self._project_context or self.cleaned_data.get('project')
        task.project = project

        if commit:
            task.save()
            assignees = self.cleaned_data.get('assignees', [])
            TaskAssignment.objects.filter(task=task).exclude(user__in=assignees).delete()
            for user in assignees:
                TaskAssignment.objects.get_or_create(task=task, user=user)
        return task
