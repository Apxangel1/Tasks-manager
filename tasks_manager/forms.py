from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm

from tasks_manager.models import Worker, Position


class WorkerForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Worker
        fields = UserCreationForm.Meta.fields

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
