from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")
    first_name = forms.CharField(required=True, label="Імʼя")
    last_name = forms.CharField(required=True, label="Прізвище")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "first_name", "last_name", "password1", "password2")
        