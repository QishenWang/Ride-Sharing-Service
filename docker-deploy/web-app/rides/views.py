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
    # if not request.session.get('is_login', None):
    #     return redirect("/rides/login")
    return render(request,'rides/index.html',locals())


# def login(request):
#     title = 'Login'
#     if request.session.get('is_login', None):  # 不允许重复登录
#         return redirect("/rides/")
#     if request.method == 'POST':
#         login_form = forms.LoginForm(request.POST)
#         error_message = 'Something went wrong...'
#         if login_form.is_valid():
#             username = login_form.cleaned_data.get('username')
#             password = login_form.cleaned_data.get('password')
#             print("!!!!!!!!!!!Here", username)
#             try:
#                 user = User.objects.get(username=username)
#                 print("!!!!!!!!!!!Here", user.username)
#                 print("!!!!!!!!!!!Here", user.password)
#             except:
#                 error_message = 'The username does not exist！'
#                 return render(request, 'rides/login.html', locals())

#             if user.password == password:
#                 request.session['is_login'] = True
#                 request.session['username'] = username
#                 return redirect("/rides/")
#             else:
#                 error_message = 'The password is incorrect！'
#                 return render(request, 'rides/login.html', locals())
#         else:
#             return render(request, 'rides/login.html', locals())

#     login_form = forms.LoginForm()
#     return render(request, 'rides/login.html', locals())
    # Python内置了一个locals()函数，它返回当前所有的本地变量字典，我们可以偷懒的将这作为render函数的数据字典参数值，就不用费劲去构造一个形如{'message':message, 'login_form':login_form}的字典了

# def logout(request):
#     if not request.session.get('is_login', None):
#         # 如果本来就未登录，也就没有登出一说
#         return redirect("/rides/login")
#     request.session.flush()
#     return render(request, 'rides/logout.html', locals())

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
            #print(same_user)
            if same_user.exists():
                # query set is not empty, same as "if sam_user:"
                error_message = "This user name is taken, try another one!"
                return render(request, 'rides/register.html',locals())
            if password != password_repeat:
                error_message = "Password does not match the password repeat!"
                return render(request, 'rides/register.html', locals())
            # add the user if all correct
            print("!!!!!!!!!!!Here", password)
            new_user = User.objects.create_user(username=username,password=password)
            print("!!!!!!!!!!!Here", new_user.password)
            new_user.save()
            return redirect("/rides/login")
        else:
            return render(request, 'rides/register.html', locals())

    register_form = forms.RegisterForm()
    return render(request, 'rides/register.html', locals())
