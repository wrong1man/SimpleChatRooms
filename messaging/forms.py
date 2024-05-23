from django import forms
from .models import User

class BaseUserSerializer_form(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
