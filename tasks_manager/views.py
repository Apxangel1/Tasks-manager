import json
from json import JSONDecodeError

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.views import generic, View
from django.http import JsonResponse
from django.db.models import Count

from .forms import WorkerForm, ProfileEditForm, ProjectForm, TaskForm, ManualWorkerCreationForm
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

class WorkerRegisterView(generic.CreateView):
    model = Worker
    form_class = WorkerForm
    template_name = "authentication/sign-up.html"
    success_url = "index"


class ManualWorkerRegisterView(LoginRequiredMixin, generic.CreateView):
    model = Worker
    form_class = ManualWorkerCreationForm
    template_name = "manager/worker/create.html"
    success_url = reverse_lazy("worker_created")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_team'] = self.request.user.team
        context['position_ids'] = Position.objects.filter(team=self.request.user.team)
        return context

    def test_func(self):
        return self.request.user.position.name == "Creator"

    def form_valid(self, form):
        user = form.save(commit=False)
        user.team = self.request.user.team

        default_position, _ = Position.objects.get_or_create(name="Worker", team=user.team)
        user.position = default_position

        user.save()

        return render(self.request, 'manager/worker/create_done.html', {
            'username': user.username,
            'password': form.cleaned_data['password1']
        })

class WorkerCreatedView(generic.TemplateView):
    template_name = "manager/worker/create_done.html"

@login_required
def create_position(request):
    if request.method == "POST":
        name = request.POST.get("objectName")
        position = Position.objects.create(name=name, team=request.user.team)
        return JsonResponse({"id": position.pk, "name": position.name})
    return JsonResponse({"error": "Invalid method"}, status=405)

@login_required
def delete_positions(request):
    if request.method != "POST":
        return JsonResponse({"error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        ids = data.get("position_ids", [])
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    # Annotate with the count of assigned workers using default related name
    positions = Position.objects.filter(pk__in=ids, team=request.user.team).annotate(worker_count=Count("worker"))

    # Find positions with any assigned workers
    positions_with_workers = positions.filter(worker_count__gt=0)

    if positions_with_workers.exists():
        names = ", ".join(pos.name for pos in positions_with_workers)
        return JsonResponse({
            "warning": f"Cannot delete the following positions because they are still assigned to workers: {names}"
        }, status=400)

    positions.delete()
    return JsonResponse({"success": True})

@login_required
def delete_own_account(request):
    if request.method == "POST":
        user = request.user
        logout(request)  # Log them out before deleting
        user.delete()
        return JsonResponse({"success": True})

    return JsonResponse({"error": "Invalid method"}, status=405)

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

@method_decorator(csrf_protect, name='dispatch')
class ProjectDeleteView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')

            if not project_id:
                return JsonResponse({'success': False, 'error': 'No project ID provided'}, status=400)

            project = Project.objects.get(pk=project_id)
            project.delete()

            return JsonResponse({'success': True})

        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

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

    def get_success_url(self):
        return reverse("project", kwargs={"project_pk": self.kwargs["project_pk"]})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['task_types'] = TaskType.objects.filter(team=self.request.user.team)
        return context

    def form_valid(self, form):
        form.instance.team = self.request.user.team
        form.instance.project = Project.objects.get(pk=self.kwargs['project_pk'])
        form.instance.is_completed = False

        return super().form_valid(form)

@method_decorator(csrf_protect, name='dispatch')
class TaskDeleteView(View):
    def post(self, request, project_pk):
        try:
            data = json.loads(request.body)
            task_id = data.get('task_id')

            if not task_id:
                return JsonResponse({'success': False, 'error': 'No task ID provided'}, status=400)

            task = Task.objects.get(pk=task_id, project_id=project_pk)
            task.delete()

            return JsonResponse({'success': True})

        except Task.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Task not found'}, status=404)

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

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

class DeleteTaskTypesView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            type_ids = data.get("type_ids", [])
            if not type_ids:
                return JsonResponse({"error": "No task types selected."}, status=400)

            types = TaskType.objects.filter(pk__in=type_ids, team=request.user.team)

            used_types = types.annotate(task_count=Count("tasks")).filter(task_count__gt=0)
            if used_types.exists():
                max_names = 3
                names = [t.name for t in used_types]
                if len(names) > max_names:
                    displayed_names = ', '.join(names[:max_names]) + f' and {len(names) - max_names} more...'
                else:
                    displayed_names = ', '.join(names)

                return JsonResponse({
                    "warning": f"Cannot delete these types because they are assigned to tasks: {displayed_names}"
                }, status=400)

            types.delete()

            return JsonResponse({"success": True})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid data."}, status=400)

@method_decorator(require_POST, name='dispatch')
class AddAssigneesView(View):
    def post(self, request, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        assignee_ids = request.POST.getlist('assignees[]')
        workers = Worker.objects.filter(pk__in=assignee_ids)

        task.assignees.add(*workers)

        return JsonResponse({'success': True, 'added': [w.pk for w in workers]})

class RemoveAssigneeView(View):
    def post(self, request, project_pk, task_pk):
        task = get_object_or_404(Task, pk=task_pk, project__pk=project_pk)

        try:
            data = json.loads(request.body)
            worker_id = data.get('worker_id')
            if not worker_id:
                return JsonResponse({'error': 'Missing worker_id'}, status=400)

            worker = get_object_or_404(Worker, pk=worker_id)
            task.assignees.remove(worker)
            return JsonResponse({'success': True})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

class MyTasksView(generic.ListView):
    model = Task
    template_name = "dashboard/my_tasks.html"

    def get_queryset(self, **kwargs):
        return Task.objects.filter(assignees__pk=self.request.user.pk)

class ToggleTaskCompletionView(View):
    def post(self, request, project_pk, task_pk):
        task = get_object_or_404(Task, pk=task_pk)
        task.is_completed = not task.is_completed
        task.save()
        return redirect('task_details', project_pk=task.project.pk, task_pk=task.pk)
