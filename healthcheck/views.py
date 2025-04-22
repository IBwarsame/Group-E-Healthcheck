from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm
from .decorators import anonymous_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django import forms

# Your existing views
def index(request):
    return redirect("home")

@login_required
def home(request):
    context = {
        'user': request.user,
    }
    return render(request, 'home.html', context)

@anonymous_required
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Successfully registered!')
            return redirect("home")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

@anonymous_required
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Logged in successfully!')
                return redirect("home")
    else:
        form = AuthenticationForm(request)
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect("home")

@login_required
def profile_view(request):
    if request.method == 'POST':
        print("POST Data:", request.POST)
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.userprofile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile')
        else:
            print("User Form Errors:", user_form.errors)
            print("Profile Form Errors:", profile_form.errors)
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.userprofile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'profile.html', context)

@login_required
def test_view(request):
    template = loader.get_template("test.html")
    context = {
        "title": "this is a test page",
    }
    return HttpResponse(template.render(context, request))

@login_required
def card_form_view(request):
    if request.method == 'POST':
        team = request.POST.get('team')
        code_base_health = request.POST.get('code_base_health')
        stakeholder_engagement = request.POST.get('stakeholder_engagement')
        release_process = request.POST.get('release_process')
        technical_debt = request.POST.get('technical_debt')
        teamwork_collaboration = request.POST.get('teamwork_collaboration')
        delivery_speed = request.POST.get('delivery_speed')
        
        # Here you would save the votes to your database
        # For example:
        # Vote.objects.create(
        #     team=team,
        #     user=request.user,
        #     code_base_health=code_base_health,
        #     stakeholder_engagement=stakeholder_engagement,
        #     release_process=release_process,
        #     technical_debt=technical_debt,
        #     teamwork_collaboration=teamwork_collaboration,
        #     delivery_speed=delivery_speed
        # )
        
        messages.success(request, "Your votes have been submitted successfully!")
        return redirect('team_dashboard')
    
    context = {
        "title": "Team Health Check Voting",
    }
    return render(request, "card_form.html", context)

@login_required
def dashboard_view(request):
    context = {
        'user': request.user,
        'title': 'Dashboard'
    }
    return render(request, 'dashboard.html', context)

@login_required
def team_dashboard_view(request):
    # In a real application, you would fetch the voting data from your database
    # For example:
    # teams = Team.objects.all()
    # selected_team = request.GET.get('team', teams.first().id if teams.exists() else None)
    # votes = Vote.objects.filter(team=selected_team)
    
    context = {
        'title': 'Team Leader Dashboard',
    }
    return render(request, 'team_dashboard.html', context)

# Custom password reset forms
class UserPasswordResetForm(PasswordResetForm):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )

class UserSetPasswordForm(forms.Form):
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'New password'
        })
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm new password'
        })
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password1"])
        if commit:
            self.user.save()
        return self.user

# Password reset views - replace your existing forgot_password view
@anonymous_required
def password_reset_request(request):
    if request.method == "POST":
        form = UserPasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            associated_users = User.objects.filter(Q(email=email))
            if associated_users.exists():
                for user in associated_users:
                    subject = "Password Reset Requested"
                    email_template_name = "password_reset_email.html"
                    context = {
                        "email": user.email,
                        "domain": request.META['HTTP_HOST'],
                        "site_name": "Your Site",
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        "user": user,
                        "token": default_token_generator.make_token(user),
                        "protocol": "https" if request.is_secure() else "http",
                    }
                    email_message = render_to_string(email_template_name, context)
                    try:
                        send_mail(subject, email_message, "noreply@yoursite.com", [user.email], fail_silently=False)
                    except BadHeaderError:
                        return HttpResponse("Invalid header found.")
                    return redirect("password_reset_done")
            messages.error(request, "An invalid email has been entered.")
    else:
        form = UserPasswordResetForm()
    return render(request, "password_reset.html", {"form": form})

@anonymous_required
def password_reset_done(request):
    return render(request, "password_reset_done.html")

@anonymous_required
def password_reset_confirm(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = UserSetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                messages.success(request, "Your password has been set. You may now log in with your new password.")
                return redirect("password_reset_complete")
        else:
            form = UserSetPasswordForm(user)
        return render(request, "password_reset_confirm.html", {"form": form})
    else:
        return render(request, "password_reset_invalid.html")

@anonymous_required
def password_reset_complete(request):
    return render(request, "password_reset_complete.html")

# Keep this for backward compatibility if needed
def forgot_password(request):
    return redirect('password_reset')
