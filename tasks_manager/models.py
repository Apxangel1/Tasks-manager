from django.db import models
from django.contrib.auth.models import AbstractUser


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(default="Team's description.")

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

class Position(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "team")

    def __str__(self):
        return f"{self.name} ({self.team.name})"

class Worker(AbstractUser):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.PROTECT)

    class Meta:
        ordering = ["first_name", "last_name"]
        verbose_name_plural = "workers"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

class Project(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="Project's description.")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="owned_projects"
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "team")

class TaskType(models.Model):
    name = models.CharField(max_length=255)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='task_types'
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "team")

    def __str__(self):
        return self.name

class Task(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(default="Task's description.")
    deadline = models.DateTimeField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    task_type = models.ForeignKey(
        TaskType,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="tasks"
    )
    assignees = models.ManyToManyField(
        Worker,
        related_name="tasks",
        blank=True
    )

    class Priority(models.TextChoices):
        LOW = "L", "Low"
        MEDIUM = "M", "Medium"
        HIGH = "H", "High"
        URGENT = "U", "Urgent"

    priority = models.CharField(
        max_length=6,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )

    class Meta:
        ordering = ["name"]
        unique_together = ("name", "project")
