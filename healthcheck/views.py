from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader


def index(request):
    return HttpResponse("<a href='/register'>Register</a><br/><a href='/login'>Log in</a>")

def register(request):
    return render(request, "register.html")
  
def login(request):
    return render(request, "login.html")

def test(request):
    template = loader.get_template("test.html")
    context = {
        "title": "this is a test page",
    }
    
    return HttpResponse(template.render(context, request))