from typing import Type

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form extending Django's built-in UserCreationForm.
    Ensures that an email address is explicitly required during signup, 
    allowing for reliable password recovery functionality.
    """
    email = forms.EmailField(
        required=True, 
        help_text="Required. Tell us your email to reset password if forgotten."
    )

    class Meta(UserCreationForm.Meta):
        model: Type[User] = User
        fields = UserCreationForm.Meta.fields + ('email',)
