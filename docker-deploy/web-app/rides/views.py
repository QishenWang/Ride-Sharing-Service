from django.shortcuts import render
from django.http import HttpResponse


#def index(request):
#    return HttpResponse("Hello, world. You're at the rides index.")

def login(request):
    return render(request, 'rides/login.html')

def register(request):
    return render(request, 'rides/register.html')

def register_request(request):
    return HttpResponse("You're requesting for registration.")

# Create your views here.
