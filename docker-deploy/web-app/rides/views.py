from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import User, Driver, Ride
from . import forms
from . import models


def index(request):
    return render(request,'rides/index.html',locals())


def login(request):
    title = 'Login'
    if request.method == 'POST':
        login_form = forms.LoginForm(request.POST)
        error_message = 'Something went wrong...'
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            try:
                user = User.objects.get(user_name=username)
            except:
                error_message = 'The username does not exist！'
                return render(request, 'rides/login.html', locals())

            if user.user_password == password:
                return redirect('/rides/')
            else:
                error_message = 'The password is incorrect！'
                return render(request, 'rides/login.html', locals())
        else:
            return render(request, 'rides/login.html', locals())

    login_form = forms.LoginForm()
    return render(request, 'rides/login.html', locals())
    # Python内置了一个locals()函数，它返回当前所有的本地变量字典，我们可以偷懒的将这作为render函数的数据字典参数值，就不用费劲去构造一个形如{'message':message, 'login_form':login_form}的字典了


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
            same_user = User.objects.filter(user_name__exact=username)
            #print(same_user)
            if same_user.exists():
                # query set is not empty, same as "if sam_user:"
                error_message = "This user name is taken, try another one!"
                return render(request, 'rides/register.html',locals())
            if password != password_repeat:
                error_message = "Password does not match the password repeat!"
                return render(request, 'rides/register.html', locals())
            # add the user if all correct
            new_user = User(user_name=username, user_password=password)
            new_user.save()
            return redirect('/rides/login')
        else:
            return render(request, 'rides/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'rides/register.html', locals())
