from django.views import generic

from .models import Task


class TasksListView(generic.ListView):
    model = Task
    context_object_name = "tasks_list"
    template_name = "base.html"
