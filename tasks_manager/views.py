from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import login
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views import generic, View
from django.http import JsonResponse

from .forms import WorkerForm, ProfileEditForm, ProjectForm, TaskForm
from .models import Task, Worker, Project, Team, Position, TaskType


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

class SidebarProjectsView(LoginRequiredMixin, generic.TemplateView):
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
    success_url = reverse_lazy("change_password_done")

class PasswordChangeDone(generic.TemplateView):
    model = Worker
    template_name = "authentication/password-change-done.html"
    success_url = reverse_lazy("index")

class SelfRegisterView(generic.CreateView):
    form_class = WorkerForm
    template_name = "authentication/sign-up.html"
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save(commit=False)

        team_name = form.cleaned_data.get("team_name")
        team = Team.objects.create(name=team_name.strip())
        user.team = team

        creator_team, _ = Position.objects.get_or_create(
            name="Creator",
            team=team
        )

        user.position = creator_team
        user.save()
        login(self.request, user)
        return redirect(self.success_url)

class ProjectCreateView(generic.CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "manager/project/create.html"
    success_url = reverse_lazy("projects")

    def form_valid(self, form):
        form.instance.team = self.request.user.team
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["team"] = self.request.user.team
        return kwargs

class ProjectListView(generic.ListView):
    model = Project
    context_object_name = "projects_list"
    template_name = "manager/project/list.html"

class ProjectDetailView(generic.DetailView):
    model = Project
    template_name = "manager/project/detail.html"

    def get_object(self, queryset=None):
        project_pk = self.kwargs.get('project_pk')
        return get_object_or_404(Project, pk=project_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["task_list"] = Task.objects.filter(project=self.object)
        return context

class TaskCreateView(generic.CreateView):
    model = Task
    template_name = "manager/tasks/create.html"
    form_class = TaskForm
    success_url = reverse_lazy("projects")

    def form_valid(self, form):
        form.instance.team = self.request.user.team
        form.instance.project = Project.objects.get(pk=self.kwargs['pk'])
        form.instance.is_completed = False

        return super().form_valid(form)

class TasksListView(LoginRequiredMixin, generic.ListView):
    model = Task
    context_object_name = "task_list"
    template_name = "manager/tasks/list.html"

class TaskDetailView(generic.DetailView):
    model = Task
    template_name = "manager/tasks/detail.html"

    def get_object(self, queryset=None):
        task_pk = self.kwargs.get('task_pk')
        return get_object_or_404(Task, pk=task_pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["workers_list"] = Worker.objects.filter(team=self.request.user.team)
        return context

class CreateTaskTypeView(View):
    def post(self, request):
        name = request.POST.get('objectName')
        team = request.user.team
        if name:
            category = TaskType.objects.create(name=name, team=team)
            return JsonResponse({'id': category.id, 'name': category.name}, status=200)
        return JsonResponse({'error': 'Name is required'}, status=400)

@method_decorator(require_POST, name='dispatch')
class AddAssigneesView(View):
    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        assignee_ids = request.POST.getlist('assignees[]')
        workers = Worker.objects.filter(pk__in=assignee_ids)

        task.assignees.add(*workers)

        return JsonResponse({'success': True, 'added': [w.pk for w in workers]})

class MyTasksView(generic.ListView):
    model = Task
    template_name = "manager/tasks/list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tasks_list"] = Task.objects.filter(assignees=self.request.user)
        return context
