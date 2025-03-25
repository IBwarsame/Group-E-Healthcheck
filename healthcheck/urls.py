from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.register, name="Register"),
    path("login", views.login, name="Login"),
    path("test", views.test, name="Test")
]