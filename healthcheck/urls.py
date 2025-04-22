from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),
    path("card-form/", views.card_form_view, name="card_form"),
    path("team-dashboard/", views.team_dashboard_view, name="team_dashboard"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("about/", views.about_view, name="about"),
    
    # Password reset URLs
    path("forgot-password/", views.password_reset_request, name="password_reset"),
    path("password-reset/done/", views.password_reset_done, name="password_reset_done"),
    path("password-reset-confirm/<uidb64>/<token>/", views.password_reset_confirm, name="password_reset_confirm"),
    path("password-reset-complete/", views.password_reset_complete, name="password_reset_complete"),
]
