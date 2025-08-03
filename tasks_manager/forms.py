from django.forms import ModelForm, CharField, TextInput, DateTimeInput
from django.contrib.auth.forms import (
    UserCreationForm,
    UserChangeForm,
    PasswordChangeForm
)

from tasks_manager.models import Worker, Project, Task


class WorkerForm(UserCreationForm):
    team_name = CharField(
        max_length=255,
        label="Name of your team",
        widget=TextInput()
    )

    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields + ("team_name",)

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
        fields = ["name", "description"]

    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop("team", None)  # <- safely pop the 'team' kwarg
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")

        if self.team and Project.objects.filter(name=name, team=self.team).exists():
            self.add_error("name", "A project with this name already exists in your team.")

        return cleaned_data

class TaskForm(ModelForm):
    class Meta:
        model = Task
        fields = ["name", "description", "deadline", "task_type", "assignees", "priority"]
        widgets = {
            'deadline': DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['deadline'].input_formats = ['%Y-%m-%dT%H:%M']