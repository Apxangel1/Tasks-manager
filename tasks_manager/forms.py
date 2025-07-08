from django.contrib.auth.forms import UserCreationForm

from tasks_manager.models import Worker, Position


class WorkerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields
