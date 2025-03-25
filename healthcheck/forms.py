from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLES, 
        required=True,
        initial='engineer'
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password1", "password2", "role"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].widget.attrs.update({
            'class': 'input-field',
        })

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            UserProfile.objects.create(user=user, role=self.cleaned_data["role"])
        return user

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True
        self.fields['email'].widget.attrs['class'] = 'input-field disabled-field'

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'instance' in kwargs and kwargs['instance']:
            self.fields['role'].initial = kwargs['instance'].role.title()
        self.fields['role'].widget.attrs.update({
            'readonly': True,
            'class': 'input-field disabled-field',
        })