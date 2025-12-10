from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('my-projects/', views.MyProjectsView.as_view(), name='my-projects'),
    path('detail/<int:project_id>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('create/', views.ProjectCreateView.as_view(), name='create-project'),
    path('add-member/<int:project_id>/', views.ProjectMemberAddView.as_view(), name='add-member'),
    path('create-task/<int:project_id>/', views.ProjectTaskCreateView.as_view(), name='create-task'),
    path('tasks/<int:task_id>/', views.TaskDetailView.as_view(), name='task-detail'),
    path('remove-member/<int:project_id>/<int:user_id>/', views.ProjectMemberRemoveView.as_view(), name='remove-member'),
    path('tasks/', views.TasksPageView.as_view(), name='tasks'),
    path('tasks/delete/<int:task_id>/', views.TaskDeleteView.as_view(), name='delete_task'),
    path('tasks/add/', views.TaskAddView.as_view(), name='add_task'),
]

