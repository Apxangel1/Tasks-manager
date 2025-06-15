from django.db import models
from django.contrib.auth.models import AbstractUser


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]


class Worker(AbstractUser):
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "workers"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(Worker, related_name="teams", blank=True)

    class Meta:
        ordering = ["name"]


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    teams = models.ManyToManyField(Team, related_name='projects', blank=True)

    class Meta:
        ordering = ["name"]


class Task(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(max_length=255, blank=True)
    deadline = models.DateTimeField(blank=True)
    is_completed = models.BooleanField(default=False)
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE)
    assignees = models.ManyToManyField(Worker, related_name="tasks", blank=True)

    class Priority(models.TextChoices):
        low = "Low"
        medium = "Medium"
        high = "High"
        urgent = "Urgent"

    priority = models.CharField(
        max_length=6,
        choices=Priority,
        default=Priority.medium
    )

    class Meta:
        ordering = ["name"]
