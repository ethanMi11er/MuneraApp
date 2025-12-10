from django.db import models
from django.db.models import CASCADE
from datetime import date

from organization.models import Organization



class Status(models.TextChoices):
    ToDo = "To Do"
    InProgress = "In Progress"
    Testing = "Testing"
    Done = "Done"


class Project(models.Model):
    project_id = models.AutoField(primary_key=True, editable=False, null=False, help_text="Project ID", verbose_name="Project ID")
    organization = models.ForeignKey(Organization, on_delete=CASCADE, related_name="projects")
    created_by = models.ForeignKey('users.User', on_delete=CASCADE, related_name="created_projects")
    project_name = models.CharField(max_length=100, null=False, help_text="Name Of Project", verbose_name="Project Name")
    project_desc = models.TextField(blank=True, null=True, help_text="Description Of Project", verbose_name="Description")
    start_date = models.DateField(blank=True, null=True, help_text="Project Start Date", verbose_name="Start Date")
    end_date = models.DateField(blank=True, null=True, help_text="Project End Date", verbose_name="End Date")
    
    
    members = models.ManyToManyField('users.User', through='ProjectMember', related_name='projects')

    def __str__(self):
        return f"{self.project_name}"


class ProjectMember(models.Model):
    class Role(models.TextChoices):
        MANAGER = "Manager", "Manager"
        MEMBER = "Member", "Member"
    
    project = models.ForeignKey(Project, on_delete=CASCADE, related_name="memberships")
    user = models.ForeignKey('users.User', on_delete=CASCADE, related_name="project_memberships")
    date_joined = models.DateField(default=date.today, help_text="Date User Joined Project", verbose_name="Joined Date")
    
    role = models.CharField(
        max_length=7,
        choices=Role.choices,
        default=Role.MEMBER,
        help_text="Users role in this member",
    )
    class Meta:
        unique_together = ("project", "user")

    def __str__(self):
        return f"{self.user} ({self.role}) @ {self.project}"


class Task(models.Model):
    task_id = models.AutoField(primary_key=True, editable=False, null=False, help_text="Task ID", verbose_name="Task ID")
    project = models.ForeignKey(Project, on_delete=CASCADE, related_name="tasks",)
    status = models.CharField(max_length=11, choices=Status.choices, help_text="Task Status", verbose_name="Status")
    task_name = models.CharField(max_length=100, null=False, help_text="Name Of Task", verbose_name="Task Name")
    task_desc = models.TextField(blank=True, null=True, help_text="Description Of Task", verbose_name="Description")
    due_date = models.DateField(blank=True, null=True, help_text="Task Due Date", verbose_name="Due Date")
    
    assignees = models.ManyToManyField('users.User', through='TaskAssignment', related_name='tasks')

    def __str__(self):
        return f"{self.task_name}: {self.status}"

class TaskAssignment(models.Model):
    task = models.ForeignKey(Task, on_delete=CASCADE, related_name="assignments")
    user = models.ForeignKey('users.User', on_delete=CASCADE, related_name="task_assignments")
    date_assigned = models.DateField(default=date.today, help_text="Date User Assigned To Task", verbose_name="Date Assigned")
    class Meta:
        unique_together = ("task", "user")

    def __str__(self):
        return f"{self.user} -> {self.task}"