from .views import TasksListView, index
from django.urls import path


urlpatterns = [
    path("", index, name="index" ),
    path("projects/<int:pk>/tasks/", TasksListView.as_view(), name="tasks"),

]
