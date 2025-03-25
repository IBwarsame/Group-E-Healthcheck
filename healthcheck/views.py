from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .forms import CustomUserCreationForm  # Add this import at the top
from .decorators import anonymous_required

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
            return redirect("home")  # Redirect to home page
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
def test_view(request):
    template = loader.get_template("test.html")
    context = {
        "title": "this is a test page",
    }
    
    return HttpResponse(template.render(context, request))