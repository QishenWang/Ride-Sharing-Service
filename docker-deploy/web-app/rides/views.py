from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.contrib.auth.models import User
from .models import Driver, Ride, ShareRecord
from . import forms
from . import models
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from datetime import datetime, timedelta, time

from django.views.generic import (ListView, DetailView, CreateView, UpdateView,
                                  DeleteView)
from django.core.mail import send_mail
from django.db.models import Q


def get_shared_rides(user):
    records = user.Sharer.all()
    ride_id = records.values_list('ride')
    return Ride.objects.filter(id__in=ride_id)
def get_shared_users(ride):
    records = ride.Ride.all()
    user_id = records.values_list('user')
    return User.objects.filter(id__in=user_id)

def get_shared_rides_id(user):
    records = user.Sharer.all()
    return records.values_list('ride')

class RideListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/index.html'  # <app>/<model>_<viewtype>.html

    def get_context_data(self, **kwargs):
        context = super(RideListView, self).get_context_data(**kwargs)
        today = datetime.now().date()
        today_start = datetime.combine(today, time())
        context['user_mode'] = True
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        context['my_rides'] = self.request.user.Owner.all().filter(
            arrival_time__gte=today_start).filter(
                is_complete=False).order_by('arrival_time')
        context['shared_rides'] = get_shared_rides(self.request.user).filter(
            arrival_time__gte=today_start).filter(
                is_complete=False).order_by('arrival_time')
        return context


class RideCreateView(LoginRequiredMixin, CreateView):
    model = Ride
    fields = [
        'ride_destination', 'is_sharable', 'arrival_time', 'passenger_number',
        'vehicle_type', 'special_request'
    ]

    def form_valid(self, form):
        form.instance.ride_owner = self.request.user
        form.instance.total_passenger_number = form.instance.passenger_number
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
        form.instance.total_passenger_number += form.instance.passenger_number - Ride.objects.filter(id=form.instance.id).first().passenger_number
        return super().form_valid(form)

    def test_func(self):
        ride = self.get_object()
        if self.request.user == ride.ride_owner and ride.ride_driver == None:
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


class DriverConfirmedListView(LoginRequiredMixin, UserPassesTestMixin,
                              ListView):
    model = Ride
    template_name = 'rides/driver.html'  # <app>/<model>_<viewtype>.html

    def test_func(self):
        if Driver.objects.filter(user=self.request.user).exists():
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DriverConfirmedListView,
                        self).get_context_data(**kwargs)
        today = datetime.now().date()
        today_start = datetime.combine(today, time())
        context['user_mode'] = False
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        context['my_rides'] = self.request.user.Driver.all().filter(
            arrival_time__gte=today_start).filter(
                is_complete=False).order_by('arrival_time')
        return context


class DriverConfirmedDetailView(LoginRequiredMixin, UserPassesTestMixin,
                                DetailView):
    model = Ride
    template_name = 'rides/driver_confirmed_ride_detail.html'

    def test_func(self):
        ride = self.get_object()
        driver_exists = Driver.objects.filter(user=self.request.user).exists()
        ride_belongs_driver = ride.ride_driver.id == self.request.user.id
        if driver_exists and ride_belongs_driver:
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DriverConfirmedDetailView,
                        self).get_context_data(**kwargs)
        context['user_mode'] = False
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        return context


@login_required
def complete_ride(request, ride_id):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = False

    ride = Ride.objects.filter(pk=ride_id).first()
    driver_exists = Driver.objects.filter(user=request.user).exists()
    ride_belongs_driver = ride.ride_driver.id == request.user.id
    if driver_exists and ride_belongs_driver:
        ride.is_complete = True
        ride.save()
    else:
        messages.error(
            request,
            f'You are not autherized for completing ride #{ride_id} !')
    return render(request, 'rides/driver_confirmed_ride_detail.html', locals())


class DriverFindListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Ride
    template_name = 'rides/driver_find_ride.html'  # <app>/<model>_<viewtype>.html

    def test_func(self):
        if Driver.objects.filter(user=self.request.user).exists():
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DriverFindListView, self).get_context_data(**kwargs)
        today = datetime.now().date()
        today_start = datetime.combine(today, time())
        context['user_mode'] = False
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()

        self_user = self.request.user
        self_driver = Driver.objects.filter(user=self.request.user).first()
        
        context['my_rides'] = Ride.objects.filter(
            ride_driver=None,
            arrival_time__gt=today_start,
            vehicle_type=self_driver.vehicle_type,
            total_passenger_number__lte=self_driver.max_passenger_number,
            special_request__in=[
                '', self_driver.special_vehicle_info
            ]).exclude(ride_owner=self_user).exclude(id__in=get_shared_rides_id(self_user)).order_by('arrival_time')
        return context


@login_required
def confirm_ride(request, ride_id):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = False

    ride = Ride.objects.filter(pk=ride_id).first()
    driver_exists = Driver.objects.filter(user=request.user).exists()
    if driver_exists:
        ride.ride_driver = request.user
        ride.save()
        send_mail(
            'Your ride is confirmed! -- The Best Amazing Rides App',
            f'Hi there!\n\nThis is an email from The Best Amazing Rides!\nYour ride #{ride.id} has been confirmed by {request.user.username}.\nEnjoy your ride!\n\nCheers!!!',
            'BestAmazingRides@outlook.com',
            [ride.ride_owner.email],
            fail_silently=False,
        )
        messages.success(request,
                         f'You have successfully confirmed ride #{ride_id} !')
        for sharer in get_shared_users(ride):
            send_mail(
            'Your ride is confirmed! -- The Best Amazing Rides App',
            f'Hi there!\n\nThis is an email from The Best Amazing Rides!\nYour ride #{ride.id} has been confirmed by {request.user.username}.\nEnjoy your ride!\n\nCheers!!!',
            'BestAmazingRides@outlook.com',
            [sharer.email],
            fail_silently=False,
        )
    else:
        messages.error(
            request,
            f'You are not autherized for confirming ride #{ride_id} !')
    self_user = request.user
    self_driver = Driver.objects.filter(user=request.user).first()
    today = datetime.now().date()
    today_start = datetime.combine(today, time())
    my_rides = Ride.objects.filter(
        ride_driver=None,
        arrival_time__gt=today_start,
        vehicle_type=self_driver.vehicle_type,
        total_passenger_number__lte=self_driver.max_passenger_number,
        special_request__in=[
            '', self_driver.special_vehicle_info
        ]).exclude(ride_owner=self_user).exclude(id__in=get_shared_rides_id(self_user)).order_by('arrival_time')
    return render(request, 'rides/driver_find_ride.html', locals())


class DriverHistoryListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Ride
    template_name = 'rides/driver_history.html'  # <app>/<model>_<viewtype>.html

    def test_func(self):
        if Driver.objects.filter(user=self.request.user).exists():
            return True
        return False

    def get_context_data(self, **kwargs):
        context = super(DriverHistoryListView, self).get_context_data(**kwargs)
        context['user_mode'] = False
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        context['my_rides'] = self.request.user.Driver.all().filter(
            is_complete=True).order_by('-arrival_time')
        return context

#TODO: share record refactor !!!!!
class RideHistoryListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/ride_history.html'  # <app>/<model>_<viewtype>.html

    def get_context_data(self, **kwargs):
        context = super(RideHistoryListView, self).get_context_data(**kwargs)
        context['user_mode'] = True
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        context['my_rides'] = self.request.user.Owner.all().filter(
            is_complete=True).order_by('arrival_time')
        return context


class ShareListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/ridesharer_list.html'

    def get_context_data(self, **kwargs):
        my_rides = self.request.POST.get('my_rides', None)
        context = super(ShareListView, self).get_context_data(**kwargs)
        context['user_mode'] = True
        context['my_rides'] = my_rides
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        return context


def sharer_search(request):
    title = 'Sharer Search'
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = True
    if request.method == 'GET':
        search_form = forms.SharerSearchForm()
        # return render(request, 'rides/sharer_search.html',
        #               {'search_form': search_form})
        return render(request, 'rides/sharer_search.html', locals())
    if request.method == 'POST':
        search_form = forms.SharerSearchForm(request.POST)
        if search_form.is_valid():
            sharer_destination = search_form.data.get('sharer_destination')
            earliest_arrival_time = search_form.data.get(
                'earliest_arrival_time')
            latest_arrival_time = search_form.data.get('latest_arrival_time')
            passenger_number = search_form.data.get('passenger_number')
            self_user = request.user
            today = datetime.now().date()
            today_start = datetime.combine(today, time())
            my_rides = Ride.objects.filter(
                ride_driver=None,
                arrival_time__gt=today_start,
                arrival_time__gte=earliest_arrival_time,
                arrival_time__lte=latest_arrival_time,
                #passenger_number__lte=self_driver.max_passenger_number,
                ride_destination__contains=sharer_destination,
                is_sharable=True).filter(
                    Q(ride_sharer1=None) | Q(ride_sharer2=None)
                    | Q(ride_sharer3=None)
                    | Q(ride_sharer4=None)).exclude(
                        ride_owner=self_user).exclude(
                            ride_sharer1=self_user).exclude(
                                ride_sharer2=self_user).exclude(
                                    ride_sharer3=self_user).exclude(
                                        ride_sharer4=self_user).order_by(
                                            'arrival_time')
            return render(request, 'rides/ridesharer_list.html', locals())
        return render(request, 'rides/sharer_search.html', locals())


@login_required
def join_ride(request, ride_id, passenger_num):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = False

    # TODO: Check passanger number?????
    # open & sharable & 有位置 & 他自己本来没在里面（不是driver/sharer/owner）
    ride = Ride.objects.filter(pk=ride_id).first()

    valid_share = (ride.ride_driver
                   == None) and (not ride.is_complete) and (ride.is_sharable)
    has_seat = (ride.ride_sharer1 == None) or (ride.ride_sharer2 == None) or (
        ride.ride_sharer3 == None) or (ride.ride_sharer4 == None)
    not_related_ride = (ride.ride_owner != request.user) and (
        ride.ride_sharer1 !=
        request.user) and (ride.ride_sharer2 != request.user) and (
            ride.ride_sharer3 != request.user) and (ride.ride_sharer4 !=
                                                    request.user)
    if valid_share and has_seat and not_related_ride:
        if not ride.ride_sharer1:
            ride.ride_sharer1 = request.user
        elif not ride.ride_sharer2:
            ride.ride_sharer2 = request.user
        elif not ride.ride_sharer3:
            ride.ride_sharer3 = request.user
        elif not ride.ride_sharer4:
            ride.ride_sharer4 = request.user
        ride.passenger_number = ride.passenger_number + passenger_num
        ride.save()
        messages.success(request,
                         f'You have successfully joined ride #{ride_id} !')
    else:
        messages.error(
            request, f'You are not autherized for joining ride #{ride_id} !')

    return render(request, 'rides/index.html', locals())
