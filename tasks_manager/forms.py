from django.forms import ModelForm, CharField, TextInput
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from tasks_manager.models import Worker, Project, Task


class WorkerForm(UserCreationForm):
    organization_name = CharField(
        max_length=255,
        label="Organization name",
        widget=TextInput()
    )

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + ("organization_name",)

class ProfileEditForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = Worker
        fields = ("first_name", "last_name", "username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'password' in self.fields:
            self.fields.pop('password')
        for field in self.fields.values():
            field.required = False

class ProfilePasswordChangeForm(PasswordChangeForm):
    pass

class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "deadline", "task_type", "assignees", "priority"]