from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Driver, Ride
from . import forms
from . import models

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)

class RideListView(ListView):
    model = Ride
    template_name = 'rides/index.html'  # <app>/<model>_<viewtype>.html
    ordering = ['-arrival_time']
    context_object_name = 'my_rides'
   

@login_required
def index(request):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = True
    my_rides = Ride.objects.filter(ride_owner=request.user)
    for ride in my_rides:
        print(ride.ride_owner.username)
    print("123333")
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
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = True
    if request.method == 'POST':
        driver = Driver.objects.create(user=request.user)
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
