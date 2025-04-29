from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile, Team, TeamMembership, Department

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(required=True, max_length=30)
    last_name = forms.CharField(required=True, max_length=30)
    email = forms.EmailField(required=True)
    role = forms.ChoiceField(
        choices=UserProfile.ROLES,
        required=True,
        initial='engineer'
    )

    team = forms.ModelChoiceField(
        queryset=Team.objects.all().order_by('name'),
        required=True,
        empty_label="Select your team",
        help_text="Select the team you belong to."
    )
    
    department = forms.ModelChoiceField(
        queryset=Department.objects.all().order_by('name'),
        required=False,
        empty_label="Select your department",
    )

    class Meta:
        model = User

        fields = ["username", "first_name", "last_name", "email", "password1", "password2", "role", "team", "department"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['role'].widget.attrs.update({
            'class': 'input-field',
        })
        self.fields['team'].widget.attrs.update({
            'class': 'input-field',
        })
        self.fields['team'].label = "Primary Team"
        
        self.fields['department'].widget.attrs.update({'class': 'input-field'})
        self.fields['department'].label = "Primary Department"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")

        if role == 'seniorManager':
            cleaned_data['department'] = None
            cleaned_data['team'] = None
            if 'department' in self._errors:
                del self._errors['department']
            if 'team' in self._errors:
                del self._errors['team']
        else:
            department = cleaned_data.get("department")
            team = cleaned_data.get("team")

            if department and team:
                if team.department != department:
                    self.add_error('team', f"Team '{team.name}' does not belong to the selected department '{department.name}'.")

            if not team:
                self.add_error('team', 'Team selection is required for this role.')


        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]

        if commit:
            user.save()
            
            selected_department = self.cleaned_data.get("department")
            selected_role = self.cleaned_data["role"]

            UserProfile.objects.create(
                user=user,
                role=selected_role,
                department=selected_department
            )

            if selected_role != 'seniorManager':
                selected_team = self.cleaned_data.get("team")
                if selected_team:
                    TeamMembership.objects.create(user=user, team=selected_team)
                else:
                    print(f"Warning: No team selected for non-senior manager user {user.username}")
            
        
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