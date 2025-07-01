from .views import TasksListView, index
from django.urls import path


urlpatterns = [
    path("", index, name="index" ),
    path("tasks/", TasksListView.as_view(), name="tasks"),

]
