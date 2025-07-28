from .views import (
    TasksListView,
    index,
    ProfileView,
    PasswordChange,
    SelfRegisterView,
    ProjectCreateView,
    ProjectListView,
    ProjectDetailView,
    TaskCreateView,
    PasswordChangeDone,
    CreateTaskTypeView,
    TaskDetailView,
    AddAssigneesView,
    MyTasksView
)
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", index, name="index" ),
    path("projects/create/", ProjectCreateView.as_view(), name="project_create"),
    path("projects/", ProjectListView.as_view(), name="projects"),
    path("project/<int:project_pk>/", ProjectDetailView.as_view(), name="project"),
    path("projects/<int:project_pk>/tasks/", TasksListView.as_view(), name="tasks"),
    path("projects/<int:project_pk>/tasks/create", TaskCreateView.as_view(), name="create_task"),
    path("projects/<int:project_pk>/tasks/<int:task_pk>/", TaskDetailView.as_view(), name="task_details"),
    path('create_task_type', CreateTaskTypeView.as_view(), name='create_task_type'),
    path('tasks/<int:task_pk>/add-assignees/', AddAssigneesView.as_view(), name='add_assignees'),
    path('tasks/my_tasks/', MyTasksView.as_view(), name='my_tasks'),
    path("login/", auth_views.LoginView.as_view(template_name='authentication/sign-in.html'), name='signin'),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='authentication/reset-password.html'), name='password_reset'),
    path("register/", SelfRegisterView.as_view(), name="signup"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("change_password", PasswordChange.as_view(), name="change_password"),
    path("change_password_done", PasswordChangeDone.as_view(), name="change_password_done"),
]
