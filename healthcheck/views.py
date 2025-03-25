from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("<a href='/signup'>sign up</a><br/><a href='/login'>login</a>")

def signup(request):
    return render(request, "signup.html")
  
def login(request):
    return render(request, "login.html")