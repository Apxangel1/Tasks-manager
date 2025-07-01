from django.shortcuts import render
from django.views import generic

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
