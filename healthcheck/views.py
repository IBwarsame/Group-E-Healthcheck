from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm, AuthenticationForm, PasswordResetForm
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib import messages
from .forms import CustomUserCreationForm, ProfileUpdateForm, UserUpdateForm
from .decorators import anonymous_required
from django.contrib.auth.models import User
from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.db.models import Count, Q, Case, When
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django import forms
from django.urls import reverse

# Add this line at the top of your views.py
from .models import HealthCheckSession, Team, Vote, TeamMembership, UserProfile, Department


# Your existing views
def index(request):
    return redirect("home")

@login_required
def home(request):
    # --- Get UserProfile ---
    try:
        # It's good practice to handle the case where UserProfile might not exist yet
        user_profile = request.user.userprofile
        user_role = user_profile.role
    except UserProfile.DoesNotExist:
        # Handle error appropriately - maybe log out, show error, or create profile
        messages.error(request, "User profile not found. Please contact support.")
        # Redirect or return an error response if needed
        user_profile = None
        user_role = None
        # return redirect('logout') # Example action

    # --- Get Memberships (only if profile exists) ---
    user_teams = []
    user_departments_list = []
    if user_profile: # Check if profile exists before querying memberships
        memberships = TeamMembership.objects.filter(
            user=request.user
        ).select_related(
            'team', 'team__department'
        ).order_by(
            'team__department__name', 'team__name'
        )
        user_departments = set()
        if memberships.exists():
            for membership in memberships:
                user_teams.append(membership.team.name)
                if membership.team.department:
                    user_departments.add(membership.team.department.name)
        user_departments_list = sorted(list(user_departments))

    # --- Update Context ---
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'user_role': user_role, # Keep this too, might be useful elsewhere
        'user_teams': user_teams,
        'user_departments': user_departments_list,
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
        
        if 'password_change' in request.POST:
            # Password change form was submitted
            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                # Update the session to prevent the user from being logged out
                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated successfully!')
                return redirect('profile')
            else:
                # If form is invalid, we'll show the same form with errors
                user_form = UserUpdateForm(instance=request.user)
                profile_form = ProfileUpdateForm(instance=request.user.userprofile)
        else:
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
        password_form = PasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'password_form': password_form,
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
def dashboard_view(request):
    context = {
        'user': request.user,
        'title': 'Dashboard'
    }
    return render(request, 'dashboard.html', context)

@login_required
def team_dashboard_view(request):
    # Get user profile and role
    user_profile = request.user.userprofile
    user_role = user_profile.role
    user_department = user_profile.department # Dept Leader's assigned dept

    # --- Determine Relevant Departments for Filtering ---
    all_departments = Department.objects.all()
    relevant_departments = all_departments # Default for Senior Manager / Admin

    if user_role == 'departmentLeader':
        if user_department:
            # Dept Leaders only see their own department
            relevant_departments = Department.objects.filter(id=user_department.id)
        else:
            # Dept Leader not assigned to a department - show none? Or all? Show none for safety.
            messages.warning(request, "You are not assigned to a department. Please contact an administrator.")
            relevant_departments = Department.objects.none()
    elif user_role in ['engineer', 'teamLeader']:
        # Engineers/Team Leaders see departments they belong to via team memberships
        user_department_ids = Team.objects.filter(
            teammembership__user=request.user,
            department__isnull=False
        ).values_list('department_id', flat=True).distinct()
        relevant_departments = Department.objects.filter(id__in=list(user_department_ids))
    # Add logic for Senior Manager if they should see all or specific ones

    # --- Get Selected Department from Request ---
    selected_department_id = request.GET.get('department')
    selected_department = None

    # --- Filter Teams based on Department and User Scope ---
    teams_queryset = Team.objects.select_related('department') # Base queryset

    # Validate and apply selected department filter
    if selected_department_id:
        try:
            # Ensure the selected department is one the user is allowed to see
            selected_department = relevant_departments.get(id=selected_department_id)
            teams_queryset = teams_queryset.filter(department=selected_department)
        except Department.DoesNotExist:
            messages.error(request, "Invalid department selected for your role.")
            selected_department_id = None # Reset invalid selection
            teams_queryset = Team.objects.none() # Show no teams if invalid dept selected
    else:
        # No department selected - apply default scope based on role
        if user_role == 'departmentLeader':
            if user_department:
                teams_queryset = teams_queryset.filter(department=user_department)
                selected_department_id = str(user_department.id) # Pre-select their department
                selected_department = user_department
            else:
                teams_queryset = Team.objects.none() # Dept leader with no dept sees no teams
        elif user_role in ['engineer', 'teamLeader']:
            # Show teams only from the departments they belong to
            teams_queryset = teams_queryset.filter(department__in=relevant_departments)
        # For Senior Manager, default might be to show all teams (no additional filter needed here)

    all_teams_in_scope = teams_queryset.order_by('name')

    # --- Session and Vote Filtering Logic ---
    all_sessions = HealthCheckSession.objects.all().order_by('-start_date')
    selected_team_id = request.GET.get('team')
    selected_session_id = request.GET.get('session')
    my_votes_only = request.GET.get('my_votes_only')

    selected_team = None
    selected_session = None
    display_data = []
    is_filtered_my_votes = bool(my_votes_only)

    # Default team selection (first team *within the current scope*)
    if not selected_team_id and all_teams_in_scope.exists():
        selected_team_id = all_teams_in_scope.first().id

    # Default session selection
    if not selected_session_id and all_sessions.exists():
        selected_session_id = all_sessions.first().id

    # Fetch selected objects (validate selected_team_id against all_teams_in_scope)
    try:
        if selected_team_id:
            # Ensure the selected team is within the user's allowed scope (already filtered)
            selected_team = all_teams_in_scope.get(id=selected_team_id)
        if selected_session_id:
            selected_session = HealthCheckSession.objects.get(id=selected_session_id)
    except (Team.DoesNotExist, HealthCheckSession.DoesNotExist, ValueError):
        # This error is less likely now for Team, as it's pre-filtered, but keep for Session
        messages.error(request, "Invalid team or session selected.")
        selected_team = None # Reset if team validation somehow failed
        # Don't reset department/session selection necessarily

    # --- Fetch and process vote data (remains the same) ---
    if selected_team and selected_session:
        base_query = Vote.objects.filter(
            team=selected_team,
            session=selected_session
        )
        if is_filtered_my_votes:
            base_query = base_query.filter(user=request.user)

        vote_aggregation = base_query.values('card_type').annotate(
            good_count=Count(Case(When(vote='good', then=1))),
            neutral_count=Count(Case(When(vote='neutral', then=1))),
            needs_improvement_count=Count(Case(When(vote='needs_improvement', then=1))),
            improving_count=Count(Case(When(progress='improving', then=1))),
            stable_count=Count(Case(When(progress='stable', then=1))),
            declining_count=Count(Case(When(progress='declining', then=1))),
            total_votes=Count('id')
        ).order_by('card_type')

        results_dict = {item['card_type']: item for item in vote_aggregation}
        all_card_types = Vote.CARD_TYPES
        for code, name in all_card_types:
            display_data.append({
                'code': code,
                'name': name,
                'result': results_dict.get(code)
            })

    context = {
        'title': 'Team Dashboard',
        'departments': relevant_departments, # Pass the filtered list of depts user can see
        'teams': all_teams_in_scope,       # Pass the filtered list of teams
        'sessions': all_sessions,
        'selected_department_id': selected_department_id,
        'selected_team': selected_team,
        'selected_session': selected_session,
        'selected_team_id': selected_team_id,
        'selected_session_id': selected_session_id,
        'display_data': display_data,
        'is_filtered_my_votes': is_filtered_my_votes,
        'user_role': user_role,
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

@login_required
def card_form_view(request):
    # --- Determine Teams within User's Department(s) ---

    # 1. Find the distinct IDs of departments the user belongs to via their team memberships
    user_department_ids = Team.objects.filter(
        teammembership__user=request.user,
        department__isnull=False # Only consider teams that HAVE a department
    ).values_list(
        'department_id', flat=True
    ).distinct()

    # 2. Get all teams belonging to those departments
    teams_in_user_departments = Team.objects.filter(
        department_id__in=list(user_department_ids) # Filter teams by the user's department IDs
    ).order_by('department__name', 'name') # Order by department, then team name

    # --- Default Team Selection (from the filtered list) ---
    default_team_id = None
    if teams_in_user_departments.exists():
        # Try to find the first team the user is ACTUALLY a member of within their departments
        first_membership = TeamMembership.objects.filter(
            user=request.user,
            team__in=teams_in_user_departments # Look only within the allowed teams
        ).select_related('team').order_by('team__department__name', 'team__name').first()

        if first_membership:
            default_team_id = first_membership.team.id
        else:
            # Fallback if user has memberships but maybe not in the filtered list? (unlikely)
            # Or just select the first team in their departments list
            default_team_id = teams_in_user_departments.first().id


    # --- Session Data ---
    all_sessions = HealthCheckSession.objects.all().order_by('-start_date')

    # --- POST Request Handling ---
    if request.method == 'POST':
        session_id = request.POST.get('session')
        team_id = request.POST.get('team')

        try:
            session = HealthCheckSession.objects.get(id=session_id)
            # Validate the selected team is one within the user's allowed departments
            team = teams_in_user_departments.get(id=team_id)
        except (HealthCheckSession.DoesNotExist, Team.DoesNotExist, ValueError):
            messages.error(request, 'Invalid session or team selected for your department(s).')
            # Redisplay form with error, passing the CORRECTLY filtered teams list
            context = {
                'sessions': all_sessions,
                'teams': teams_in_user_departments, # Pass the filtered list
                'card_types': Vote.CARD_TYPES,
                'default_team_id': default_team_id,
                'selected_session_id': session_id,
                'selected_team_id': team_id,
            }
            return render(request, 'card_form.html', context)

        # --- Vote processing logic (remains the same) ---
        validation_failed = False
        for card_type, card_name in Vote.CARD_TYPES:
            vote_value = request.POST.get(f'vote_{card_type}')
            progress_value = request.POST.get(f'progress_{card_type}')
            if not vote_value or not progress_value:
                 messages.error(request, f'Missing vote or progress for {card_name}.')
                 validation_failed = True

        if validation_failed:
            context = {
                'sessions': all_sessions,
                'teams': teams_in_user_departments, # Pass filtered list
                'card_types': Vote.CARD_TYPES,
                'default_team_id': default_team_id,
                'selected_session_id': session_id,
                'selected_team_id': team_id,
                'submitted_data': request.POST
            }
            return render(request, 'card_form.html', context)

        # If validation passed, save votes
        for card_type, _ in Vote.CARD_TYPES:
            vote_value = request.POST.get(f'vote_{card_type}')
            progress_value = request.POST.get(f'progress_{card_type}')
            comments = request.POST.get(f'comments_{card_type}')
            Vote.objects.update_or_create(
                user=request.user, team=team, session=session, card_type=card_type,
                defaults={'vote': vote_value, 'progress': progress_value, 'comments': comments}
            )
        # --- End vote processing ---

        messages.success(request, 'Your votes have been saved successfully!')
        redirect_url = reverse('team_dashboard') + f'?team={team.id}&session={session.id}'
        return redirect(redirect_url)

    # --- Context for GET Request ---
    context = {
        'sessions': all_sessions,
        'teams': teams_in_user_departments, # Pass the filtered list of teams
        'card_types': Vote.CARD_TYPES,
        'default_team_id': default_team_id,
    }
    # Handle case where user belongs to no departments/teams
    if not teams_in_user_departments.exists():
         messages.info(request, "You are not currently assigned to any teams within a department. Please contact an administrator.")

    return render(request, 'card_form.html', context)

# Helper for error message (optional but cleaner)
Vote.CARD_TYPES_DICT = dict(Vote.CARD_TYPES)