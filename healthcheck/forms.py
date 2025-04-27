from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm # Added PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, Team, TeamMembership # Added Team, TeamMembership

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLES,
        required=True,
        initial='engineer'
    )
    # Add the team selection field
    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        required=True, # Make it mandatory to select a team
        empty_label="Select your team", # Placeholder text
        help_text="Select the team you belong to."
    )

    class Meta:
        model = User
        # Add 'team' to the fields list
        fields = ["username", "first_name", "last_name", "email", "password1", "password2", "role", "team"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply styling to the new team field if needed
        self.fields['role'].widget.attrs.update({
            'class': 'input-field', # Assuming you have this class
        })
        self.fields['team'].widget.attrs.update({
            'class': 'input-field', # Apply consistent styling
        })
        self.fields['team'].label = "Primary Team" # Customize label if desired

    def save(self, commit=True):
        user = super().save(commit=False) # Don't commit the User yet
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save() # Save the User object first
            # Create the UserProfile
            UserProfile.objects.create(user=user, role=self.cleaned_data["role"])
            # Get the selected team
            selected_team = self.cleaned_data["team"]
            # Create the TeamMembership link
            TeamMembership.objects.create(user=user, team=selected_team)
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