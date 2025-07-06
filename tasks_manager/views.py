from django.contrib.auth import get_user_model
from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView

from .models import Task, Worker, Project


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

class TasksListView(generic.ListView):
    model = Task
    context_object_name = "tasks_list"
    template_name = "manager/tasks/list_view.html"

class DashboardView(TemplateView):
    template_name = "manager/includes/sidebar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_teams = self.request.user.teams.all()
        projects = Project.objects.filter(teams__in=user_teams).distinct()
        context['projects_list'] = projects
        return context
