from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.views.generic import TemplateView

from .forms import WorkerForm, ProfileEditForm, ProjectForm, TaskForm
from .models import Task, Worker, Project, Organization, Position


@login_required
def index(request):
    num_tasks = Task.objects.count()
    num_workers = Worker.objects.count()
    num_projects = Project.objects.count()

    num_visits = request.session.get("num_visits", 0) + 1
    request.session["num_visits"] = num_visits

    context = {
        "num_tasks": num_tasks,
        "num_workers": num_workers,
        "num_projects": num_projects,
        "num_visits": num_visits,
    }

    return render(request, "manager/index.html", context=context)

class SidebarProjectsView(LoginRequiredMixin, TemplateView):
    template_name = "manager/includes/sidebar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_teams = self.request.user.teams.all()
        projects = Project.objects.filter(teams__in=user_teams).distinct()
        context['projects_list'] = projects
        return context

class WorkerRegisterView(generic.CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = "authentication/sign-up.html"
    success_url = "index"

class ProfileView(LoginRequiredMixin, generic.UpdateView):
    model = Worker
    form_class = ProfileEditForm
    template_name = 'dashboard/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

class PasswordChange(PasswordChangeView):
    model = Worker
    template_name = "authentication/password-change.html"
    success_url = "authentication/password-change-done.html"

class SelfRegisterView(generic.CreateView):
    form_class = WorkerForm
    template_name = "authentication/sign-up.html"
    success_url = "index"

    def form_valid(self, form):
        user = form.save(commit=False)

        org_name = form.cleaned_data.get("organization_name")
        org = Organization.objects.create(name=org_name.strip())

        owner_pos, _ = Position.objects.get_or_create(name="Owner")

        user.organization = org
        user.position = owner_pos
        user.save()
        return redirect(self.success_url)

class ProjectCreateView(generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "manager/project/create.html"
    success_url = "projects/"

class ProjectListView(generic.ListView):
    model = Project
    context_object_name = "projects_list"
    template_name = "manager/project/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = "manager/project/detail.html"

class TaskCreateView(generic.CreateView):
    model = Task
    template_name = "manager/tasks/create.html"
    form_class = TaskForm
    success_url = "projects/"

    def form_valid(self, form):
        form.instance.org = self.request.user.org
        form.instance.project = Project.objects.get(pk=self.kwargs['project_id'])
        form.instance.is_completed = False

        return super().form_valid(form)

class TasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "tasks_list"
    template_name = "manager/tasks/list.html"
