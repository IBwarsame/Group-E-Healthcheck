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
from django.db.models import Count, Q, Case, When, Sum
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django import forms
from django.urls import reverse
from django.core.exceptions import PermissionDenied
import json


from .models import HealthCheckSession, Team, Vote, TeamMembership, UserProfile, Department



def index(request):
    return redirect("home")

@login_required
def home(request):

    try:

        user_profile = request.user.userprofile
        user_role = user_profile.role
    except UserProfile.DoesNotExist:

        messages.error(request, "User profile not found. Please contact support.")

        user_profile = None
        user_role = None



    user_teams = []
    user_departments_list = []
    if user_profile:
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


    context = {
        'user': request.user,
        'user_profile': user_profile,
        'user_role': user_role,
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
            teams_by_department = {}
            teams = Team.objects.filter(department__isnull=False).select_related('department').order_by('name')
            for team in teams:
                dept_id = str(team.department.id)
                if dept_id not in teams_by_department:
                    teams_by_department[dept_id] = []
                teams_by_department[dept_id].append({'id': team.id, 'name': team.name})
            teams_by_dept_json = json.dumps(teams_by_department)
    else:
        form = CustomUserCreationForm()
        
        teams_by_department = {}
        teams = Team.objects.filter(department__isnull=False).select_related('department').order_by('name')
        for team in teams:
            dept_id = str(team.department.id)
            if dept_id not in teams_by_department:
                teams_by_department[dept_id] = []
            teams_by_department[dept_id].append({'id': team.id, 'name': team.name})
        teams_by_dept_json = json.dumps(teams_by_department)
    
    return render(request, 'register.html', {'form': form, 'teams_by_dept_json': teams_by_dept_json})

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

            password_form = PasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()

                update_session_auth_hash(request, user)
                messages.success(request, 'Your password has been updated successfully!')
                return redirect('profile')
            else:

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
def team_dashboard_view(request):

    user_profile = request.user.userprofile
    user_role = user_profile.role
    user_department = user_profile.department


    all_departments = Department.objects.all()
    relevant_departments = all_departments

    if user_role == 'departmentLeader':
        if user_department:

            relevant_departments = Department.objects.filter(id=user_department.id)
        else:

            messages.warning(request, "You are not assigned to a department. Please contact an administrator.")
            relevant_departments = Department.objects.none()
    elif user_role in ['engineer', 'teamLeader']:

        user_department_ids = Team.objects.filter(
            teammembership__user=request.user,
            department__isnull=False
        ).values_list('department_id', flat=True).distinct()
        relevant_departments = Department.objects.filter(id__in=list(user_department_ids))



    selected_department_id = request.GET.get('department')
    selected_department = None


    teams_queryset = Team.objects.select_related('department')


    if selected_department_id:
        try:

            selected_department = relevant_departments.get(id=selected_department_id)
            teams_queryset = teams_queryset.filter(department=selected_department)
        except Department.DoesNotExist:
            messages.error(request, "Invalid department selected for your role.")
            selected_department_id = None
            teams_queryset = Team.objects.none()
    else:

        if user_role == 'departmentLeader':
            if user_department:
                teams_queryset = teams_queryset.filter(department=user_department)
                selected_department_id = str(user_department.id)
                selected_department = user_department
            else:
                teams_queryset = Team.objects.none()
        elif user_role in ['engineer', 'teamLeader']:

            teams_queryset = teams_queryset.filter(department__in=relevant_departments)


    all_teams_in_scope = teams_queryset.order_by('name')


    all_sessions = HealthCheckSession.objects.all().order_by('-start_date')
    selected_team_id = request.GET.get('team')
    selected_session_id = request.GET.get('session')
    my_votes_only = request.GET.get('my_votes_only')

    selected_team = None
    selected_session = None
    display_data = []
    is_filtered_my_votes = bool(my_votes_only)


    if not selected_team_id and all_teams_in_scope.exists():
        selected_team_id = all_teams_in_scope.first().id


    if not selected_session_id and all_sessions.exists():
        selected_session_id = all_sessions.first().id


    try:
        if selected_team_id:

            selected_team = all_teams_in_scope.get(id=selected_team_id)
        if selected_session_id:
            selected_session = HealthCheckSession.objects.get(id=selected_session_id)
    except (Team.DoesNotExist, HealthCheckSession.DoesNotExist, ValueError):

        messages.error(request, "Invalid team or session selected.")
        selected_team = None



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
        'departments': relevant_departments,
        'teams': all_teams_in_scope,
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


def forgot_password(request):
    return redirect('password_reset')

@login_required
def card_form_view(request):

    if request.user.userprofile.role in ['departmentLeader', 'seniorManager']:
        messages.error(request, "Your role does not have permission to submit votes.")
        return redirect('home')




    user_department_ids = Team.objects.filter(
        teammembership__user=request.user,
        department__isnull=False
    ).values_list(
        'department_id', flat=True
    ).distinct()


    teams_in_user_departments = Team.objects.filter(
        department_id__in=list(user_department_ids)
    ).order_by('department__name', 'name')


    default_team_id = None
    if teams_in_user_departments.exists():

        first_membership = TeamMembership.objects.filter(
            user=request.user,
            team__in=teams_in_user_departments
        ).select_related('team').order_by('team__department__name', 'team__name').first()

        if first_membership:
            default_team_id = first_membership.team.id
        else:


            default_team_id = teams_in_user_departments.first().id



    all_sessions = HealthCheckSession.objects.all().order_by('-start_date')


    if request.method == 'POST':
        session_id = request.POST.get('session')
        team_id = request.POST.get('team')

        try:
            session = HealthCheckSession.objects.get(id=session_id)

            team = teams_in_user_departments.get(id=team_id)
        except (HealthCheckSession.DoesNotExist, Team.DoesNotExist, ValueError):
            messages.error(request, 'Invalid session or team selected for your department(s).')

            context = {
                'sessions': all_sessions,
                'teams': teams_in_user_departments,
                'card_types': Vote.CARD_TYPES,
                'default_team_id': default_team_id,
                'selected_session_id': session_id,
                'selected_team_id': team_id,
            }
            return render(request, 'card_form.html', context)


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
                'teams': teams_in_user_departments,
                'card_types': Vote.CARD_TYPES,
                'default_team_id': default_team_id,
                'selected_session_id': session_id,
                'selected_team_id': team_id,
                'submitted_data': request.POST
            }
            return render(request, 'card_form.html', context)


        for card_type, _ in Vote.CARD_TYPES:
            vote_value = request.POST.get(f'vote_{card_type}')
            progress_value = request.POST.get(f'progress_{card_type}')
            comments = request.POST.get(f'comments_{card_type}')
            Vote.objects.update_or_create(
                user=request.user, team=team, session=session, card_type=card_type,
                defaults={'vote': vote_value, 'progress': progress_value, 'comments': comments}
            )


        messages.success(request, 'Your votes have been saved successfully!')
        redirect_url = reverse('team_dashboard') + f'?team={team.id}&session={session.id}'
        return redirect(redirect_url)


    context = {
        'sessions': all_sessions,
        'teams': teams_in_user_departments,
        'card_types': Vote.CARD_TYPES,
        'default_team_id': default_team_id,
    }

    if not teams_in_user_departments.exists():
         messages.info(request, "You are not currently assigned to any teams within a department. Please contact an administrator.")

    return render(request, 'card_form.html', context)


Vote.CARD_TYPES_DICT = dict(Vote.CARD_TYPES)

@login_required
def department_dashboard_view(request):
    try:
        user_profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        messages.error(request, "User profile not found. Please contact an administrator.")
        return redirect('home')

    user_role = user_profile.role

    if user_role not in ['departmentLeader', 'seniorManager']:
        messages.error(request, "You do not have permission to view the department dashboard.")
        return redirect('home')

    leader_department = user_profile.department
    all_departments = Department.objects.all()
    relevant_departments_for_filter = all_departments

    selected_department_id = request.GET.get('department')
    selected_department_for_view = None

    if user_role == 'departmentLeader':
        if leader_department:
            if not selected_department_id:
                selected_department_id = str(leader_department.id)
        else:
            selected_department_id = None

    if selected_department_id:
        try:
            if user_role == 'seniorManager':
                selected_department_for_view = all_departments.get(id=selected_department_id)
            elif user_role == 'departmentLeader':
                selected_department_for_view = all_departments.get(id=selected_department_id)
            else:
                selected_department_for_view = None
                selected_department_id = str(leader_department.id)

        except Department.DoesNotExist:
            messages.error(request, "Selected department not found.")
            selected_department_for_view = None
            selected_department_id = None

    teams_in_viewed_department = Team.objects.none()
    if selected_department_for_view:
        teams_in_viewed_department = Team.objects.filter(department=selected_department_for_view).order_by('name')

    sessions = HealthCheckSession.objects.all().order_by('-start_date')
    own_dept_display_data = []
    other_department_summaries = []
    selected_session_id = request.GET.get('session')
    selected_session = None

    chart_labels = []
    chart_good_perc = []
    chart_neutral_perc = []
    chart_needsimp_perc = []
    chart_datasets = []

    if not selected_session_id and sessions.exists():
        selected_session_id = sessions.first().id
    try:
        if selected_session_id:
            selected_session = HealthCheckSession.objects.get(id=selected_session_id)
    except (HealthCheckSession.DoesNotExist, ValueError):
         messages.error(request, "Invalid session selected.")
         selected_session = None
         selected_session_id = None

    if selected_session and selected_department_for_view:
        own_dept_vote_aggregation = Vote.objects.filter(
            team__department=selected_department_for_view,
            session=selected_session
        ).values('card_type').annotate(
            good_count=Count(Case(When(vote='good', then=1))),
            neutral_count=Count(Case(When(vote='neutral', then=1))),
            needs_improvement_count=Count(Case(When(vote='needs_improvement', then=1))),
            improving_count=Count(Case(When(progress='improving', then=1))),
            stable_count=Count(Case(When(progress='stable', then=1))),
            declining_count=Count(Case(When(progress='declining', then=1))),
            total_votes=Count('id')
        ).order_by('card_type')

        results_dict = {item['card_type']: item for item in own_dept_vote_aggregation}
        all_card_types = Vote.CARD_TYPES
        own_dept_display_data = []
        chart_labels, chart_good_perc, chart_neutral_perc, chart_needsimp_perc = [], [], [], []

        for code, name in all_card_types:
            current_result = results_dict.get(code)
            own_dept_display_data.append({'code': code, 'name': name, 'result': current_result})
            
            chart_labels.append(name)
            if current_result and current_result.get('total_votes', 0) > 0:
                total = float(current_result['total_votes'])
                good = current_result.get('good_count', 0)
                neutral = current_result.get('neutral_count', 0)
                good_perc = round((good / total) * 100, 1)
                neutral_perc = round((neutral / total) * 100, 1)
                needs_imp_perc = round(100.0 - good_perc - neutral_perc, 1)
                chart_good_perc.append(good_perc)
                chart_neutral_perc.append(neutral_perc)
                chart_needsimp_perc.append(needs_imp_perc)
            else:
                chart_good_perc.append(0); chart_neutral_perc.append(0); chart_needsimp_perc.append(0)

        chart_datasets = [
            {'label': '% Good', 'data': chart_good_perc, 'backgroundColor': '#28a745'},
            {'label': '% Neutral', 'data': chart_neutral_perc, 'backgroundColor': '#ffc107'},
            {'label': '% Needs Improvement', 'data': chart_needsimp_perc, 'backgroundColor': '#dc3545'},
        ]

        other_departments_queryset = all_departments.exclude(id=selected_department_for_view.id)
        other_department_summaries = [] # Reset

        for other_dept in other_departments_queryset:
            summary_aggregation = Vote.objects.filter(
                team__department=other_dept,
                session=selected_session
            ).aggregate(
                total_good=Count(Case(When(vote='good', then=1))),
                total_neutral=Count(Case(When(vote='neutral', then=1))),
                total_needs_improvement=Count(Case(When(vote='needs_improvement', then=1))),
                total_dept_votes=Count('id')
            )
            if summary_aggregation.get('total_dept_votes', 0) > 0:
                other_department_summaries.append({
                    'department_name': other_dept.name,
                    'summary': summary_aggregation
                })

    context = {
        'title': f"{selected_department_for_view.name} Dept. Summary" if selected_department_for_view else "Department Dashboard",
        'viewed_department': selected_department_for_view,
        'department': leader_department,
        'departments_for_filter': relevant_departments_for_filter,
        'teams_in_viewed_department': teams_in_viewed_department,
        'sessions': sessions,
        'selected_department_id': selected_department_id,
        'selected_session': selected_session,
        'selected_session_id': selected_session_id,
        'own_dept_display_data': own_dept_display_data,
        'other_department_summaries': other_department_summaries,
        'user_role': user_role,
        'chart_labels_json': json.dumps(chart_labels),
        'chart_datasets_json': json.dumps(chart_datasets),
    }
    return render(request, 'department_dashboard.html', context)