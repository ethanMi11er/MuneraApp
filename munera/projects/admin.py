from django.contrib import admin
from .models import Project, ProjectMember, Task, TaskAssignment

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'organization', 'start_date', 'end_date', 'created_by')

class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'date_joined')

class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_name', 'project', 'status', 'due_date')

class TaskAssignmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'user', 'date_assigned')

admin.site.register(Project, ProjectAdmin)
admin.site.register(ProjectMember, ProjectMemberAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(TaskAssignment, TaskAssignmentAdmin)
