from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User


class AuthForm(AuthenticationForm):

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            user = User.objects.create(username=username)
            user.set_password(password)
            user.save()

        return super().clean()
