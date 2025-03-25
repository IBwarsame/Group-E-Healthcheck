from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLES, 
        required=True,
        initial='engineer'
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({
            'class': 'input-field',
        })

    def save(self, commit=True):
        user = super().save(commit=True)
        user_profile = UserProfile.objects.create(
            user=user,
            role=self.cleaned_data['role']
        )
        return user