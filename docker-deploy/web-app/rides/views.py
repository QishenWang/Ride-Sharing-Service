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
from django.views.decorators.csrf import csrf_exempt


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
        context['shared_rides'] = get_shared_rides(
            self.request.user).filter(arrival_time__gte=today_start).filter(
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
        form.instance.total_passenger_number += form.instance.passenger_number - Ride.objects.filter(
            id=form.instance.id).first().passenger_number
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
        messages.warning(
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
            ]).exclude(ride_owner=self_user).exclude(
                id__in=get_shared_rides_id(self_user)).order_by('arrival_time')
        return context


@login_required
def confirm_ride(request, ride_id):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = False

    ride = Ride.objects.filter(pk=ride_id).first()
    driver_exists = Driver.objects.filter(user=request.user).exists()
    if driver_exists:
        driver = Driver.objects.get(user=request.user)
        valid_ride = (
            ride.total_passenger_number <= driver.max_passenger_number) and (
                ride.ride_driver
                == None) and (ride.vehicle_type == driver.vehicle_type) and (
                    driver.special_vehicle_info in ['', ride.special_request])
        if valid_ride:
            ride.ride_driver = request.user
            ride.save()
            send_mail(
                'Your ride is confirmed! -- The Best Amazing Rides App',
                f'Hi there!\n\nThis is an email from The Best Amazing Rides!\nYour ride #{ride.id} has been confirmed by {request.user.username}.\nEnjoy your ride!\n\nCheers!!!\nThe Best Amazing Rides App',
                'BestAmazingRides@outlook.com',
                [ride.ride_owner.email],
                fail_silently=False,
            )
            messages.success(
                request, f'You have successfully confirmed ride #{ride_id} !')
            for sharer in get_shared_users(ride):
                send_mail(
                    'Your ride is confirmed! -- The Best Amazing Rides App',
                    f'Hi there!\n\nThis is an email from The Best Amazing Rides!\nYour shared ride #{ride.id} has been confirmed by {request.user.username}.\nEnjoy your ride!\n\nCheers!!!\nThe Best Amazing Rides App',
                    'BestAmazingRides@outlook.com',
                    [sharer.email],
                    fail_silently=False,
                )
        else:
            messages.warning(
                request,
                f'You are not autherized for confirming ride #{ride_id} !')
    else:
        messages.warning(
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
        ]).exclude(ride_owner=self_user).exclude(
            id__in=get_shared_rides_id(self_user)).order_by('arrival_time')
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
        context['shared_rides'] = get_shared_rides(self.request.user).filter(
            is_complete=True).order_by('arrival_time')
        return context


class ShareListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/ridesharer_list.html'

    def get_context_data(self, **kwargs):
        my_rides = self.request.POST.get('my_rides', None)
        context = super(ShareListView, self).get_context_data(**kwargs)
        context['user_mode'] = True
        context['is_driver'] = Driver.objects.filter(
            user=self.request.user).exists()
        context['my_rides'] = my_rides
        return context


@login_required
def sharer_search(request):
    title = 'Sharer Search'
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = True
    if request.method == 'GET':
        search_form = forms.SharerSearchForm()
        return render(request, 'rides/sharer_search.html', locals())
    if request.method == 'POST':
        search_form = forms.SharerSearchForm(request.POST)
        if search_form.is_valid():
            sharer_destination = search_form.data.get('sharer_destination')
            earliest_arrival_time = search_form.data.get(
                'earliest_arrival_time')
            latest_arrival_time = search_form.data.get('latest_arrival_time')
            today = datetime.now().date()
            today_start = datetime.combine(today, time())

            passenger_number = search_form.data.get('passenger_number')
            self_user = request.user

            my_rides = Ride.objects.filter(
                ride_driver=None,
                arrival_time__gt=today_start,
                arrival_time__gte=earliest_arrival_time,
                arrival_time__lte=latest_arrival_time,
                ride_destination__contains=sharer_destination,
                is_sharable=True).exclude(id__in=get_shared_rides_id(
                    self_user)).order_by('arrival_time')
            return render(request, 'rides/ridesharer_list.html', locals())
        return render(request, 'rides/sharer_search.html', locals())


@login_required
def join_ride(request, ride_id, passenger_number):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = True

    today_start = datetime.combine(datetime.now().date(), time())
    my_rides = request.user.Owner.all().filter(
        arrival_time__gte=today_start).filter(
            is_complete=False).order_by('arrival_time')
    shared_rides = get_shared_rides(
        request.user).filter(arrival_time__gte=today_start).filter(
            is_complete=False).order_by('arrival_time')

    # open & sharable & 他自己本来没在里面（不是driver/sharer/owner）
    ride = Ride.objects.filter(pk=ride_id).first()
    share_users = get_shared_users(ride)
    not_related_ride = (not share_users.filter(id=request.user.id).exists()
                        ) and (ride.ride_owner.id != request.user.id)

    valid_share = (ride.ride_driver
                   == None) and (not ride.is_complete) and (ride.is_sharable)
    if valid_share and not_related_ride:
        share_record = ShareRecord(passenger_number=passenger_number)
        share_record.ride = ride
        share_record.user = request.user
        share_record.save()
        ride.total_passenger_number = ride.total_passenger_number + passenger_number
        ride.save()
        messages.success(request,
                         f'You have successfully joined ride #{ride_id} !')
    else:
        messages.warning(
            request, f'You are not autherized for joining ride #{ride_id} !')

    return render(request, 'rides/index.html', locals())


class RideDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Ride
    success_url = '/rides/'

    def test_func(self):
        ride = self.get_object()
        if self.request.user == ride.ride_owner:
            return True
        return False


class ShareDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ShareRecord
    success_url = '/rides/'

    def test_func(self):
        share_record = self.get_object()
        if self.request.user == share_record.user:
            return True
        return False

    def form_valid(self, form):
        # 从ride里面把total number 变小
        share_record = self.get_object()
        ride = Ride.objects.get(id=share_record.ride.id)
        ride.total_passenger_number = ride.total_passenger_number - share_record.passenger_number
        ride.save()
        return super().form_valid(form)


@login_required
def send_share_delete_id(request, ride_id):
    user_records = ShareRecord.objects.filter(user=request.user)
    share_id = user_records.get(ride=ride_id).id
    return redirect(f"/rides/{share_id}/delete_share/")


@login_required
def settings(request):
    is_driver = Driver.objects.filter(user=request.user).exists()
    user_mode = True
    if request.method == 'POST':
        u_form = forms.UserUpdateForm(request.POST, instance=request.user)

        if not is_driver:
            if u_form.is_valid():
                u_form.save()
                messages.success(request,
                                 f'Your user account has been updated!')
                return redirect('/rides/settings/')
        else:
            d_form = forms.DriverProfileForm(
                request.POST,
                request.FILES,
                instance=Driver.objects.get(user=request.user))
            if u_form.is_valid() and d_form.is_valid():
                u_form.save()
                d_form.save()
                messages.success(request,
                                 f'Your driver account has been updated!')
                return redirect('/rides/settings/')

    else:
        u_form = forms.UserUpdateForm(instance=request.user)
        if is_driver:
            d_form = forms.DriverProfileForm(instance=Driver.objects.get(
                user=request.user))

    return render(request, 'rides/settings.html', locals())