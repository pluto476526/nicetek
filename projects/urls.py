from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('create/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/update/', views.ProjectUpdateView.as_view(), name='update'),
    path('<int:pk>/complete/', views.project_complete_view, name='complete'),
    path('<int:project_id>/task/create/', views.TaskCreateView.as_view(), name='task_create'),
    path('<int:project_id>/status/', views.ProjectStatusUpdateView.as_view(), name='status_update'),
]
