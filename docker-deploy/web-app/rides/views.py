from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Driver, Ride
from . import forms
from . import models


@login_required
def index(request):
    isDriver = Driver.objects.filter(user_id=request.user).exists()
    user_mode = True
    return render(request, 'rides/index.html', locals())


def register(request):
    title = 'Register'
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        if register_form.is_valid():
            register_form.save()
            username = register_form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username} !')
            return redirect("/rides/login")
    else:
        register_form = forms.RegisterForm()
    return render(request, 'rides/register.html', locals())


@login_required
def newdriver(request):
    title = 'New Driver'
    isDriver = Driver.objects.filter(user_id=request.user).exists()
    user_mode = True
    if request.method == 'POST':
        driver = Driver.objects.create(user_id=request.user)
        form = forms.DriverProfileForm(request.POST, instance=driver)
        if form.is_valid():
            form.save()
            username = request.user.username
            messages.success(request,
                             f'Driver profile created for {username} !')
            return redirect("/rides")
    else:
        form = forms.DriverProfileForm()

    return render(request, 'rides/newdriver.html', locals())
