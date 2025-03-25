from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("<a href='/register'>Register</a><br/><a href='/login'>Log in</a>")

def register(request):
    return render(request, "register.html")
  
def login(request):
    return render(request, "login.html")