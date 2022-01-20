from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from django.contrib.auth.models import User
from .models import Driver, Ride
from . import forms
from . import models

@login_required
def index(request):
    return render(request,'rides/index.html',locals())


def register(request):
    title = 'Register'
    if request.method == 'POST':
        register_form = forms.RegisterForm(request.POST)
        error_message = 'Something went wrong...'
        if register_form.is_valid():
            username = register_form.cleaned_data.get('username')
            password = register_form.cleaned_data.get('password')
            password_repeat = register_form.cleaned_data.get('password_repeat')

            # check for unique user name
            same_user = User.objects.filter(username__exact=username)
            if same_user.exists():
                # query set is not empty, same as "if sam_user:"
                error_message = "This user name is taken, try another one!"
                return render(request, 'rides/register.html',locals())
            if password != password_repeat:
                error_message = "Password does not match the password repeat!"
                return render(request, 'rides/register.html', locals())
            # add the user if all correct
            new_user = User.objects.create_user(username=username,password=password)
            new_user.save()
            return redirect("/rides/login")
        else:
            return render(request, 'rides/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'rides/register.html', locals())
