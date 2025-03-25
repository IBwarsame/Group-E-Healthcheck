from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),  # Empty path redirects to home view
    path("home", views.home, name="home"),
    path("register", views.register_view, name="register"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("test", views.test_view, name="Test")
]