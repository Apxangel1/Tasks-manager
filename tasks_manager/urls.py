from .views import TasksListView, index, ProfileView, PasswordChange, SelfRegisterView
from django.urls import path
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", index, name="index" ),
    path("projects/<int:pk>/tasks/", TasksListView.as_view(), name="tasks"),
    path("login/", auth_views.LoginView.as_view(template_name='authentication/sign-in.html'), name='signin'),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='authentication/reset-password.html'), name='password_reset'),
    path("register/", SelfRegisterView.as_view(), name="signup"),
    path("profile", ProfileView.as_view(), name="profile"),
    path("change_password", PasswordChange.as_view(), name="change_password"),
]
