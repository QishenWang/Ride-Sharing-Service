from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Driver, Ride
from . import forms
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from datetime import datetime, timedelta, time

from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
                                  DeleteView)


class RideListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/index.html'  # <app>/<model>_<viewtype>.html

    def get_context_data(self, **kwargs):
        context = super(RideListView, self).get_context_data(**kwargs)
        today = datetime.now().date()
        today_start = datetime.combine(today, time())
        context['my_rides'] = self.request.user.Owner.all().filter(
            arrival_time__gte=today_start).order_by('arrival_time')
        context['user_mode'] = True
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        return context


class RideCreateView(LoginRequiredMixin, CreateView):
    model = Ride
    fields = [
        'ride_destination', 'is_sharable', 'arrival_time', 'passenger_number',
        'vehicle_type', 'special_request'
    ]

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(RideCreateView, self).get_context_data(**kwargs)
        context['user_mode'] = True
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        return context


class RideUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Ride
    fields = [
        'ride_destination', 'is_sharable', 'arrival_time', 'passenger_number',
        'vehicle_type', 'special_request'
    ]

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        return super().form_valid(form)

    def test_func(self):
        ride = self.get_object()
        if self.request.user == ride.ride_owner:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(RideUpdateView, self).get_context_data(**kwargs)
        context['user_mode'] = True
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        return context


# @login_required
# def index(request):
#     is_driver = Driver.objects.filter(user=request.user).exists()
#     user_mode = True
#     my_rides = Ride.objects.filter(ride_owner=request.user).order_by('-arrival_time')
#     return render(request, 'rides/index.html', locals())


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


@login_required
def driver(request):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = False
    return render(request, 'rides/driver.html', locals())
