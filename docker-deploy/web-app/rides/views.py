from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .models import User, Driver, Ride

def index(request):
    return HttpResponse("Hello, world. You're at the rides index.")


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        print(username)
        print(password)
        if password:  # 确保用户名和密码都不为空
            # 用户名字符合法性验证
            # 密码长度验证
            # 更多的其它验证.....
            try:
                user = User.objects.get(user_name=username)
            except:
                return render(request, 'rides/login.html')
            if user.user_password == password:
                return HttpResponseRedirect(reverse('rides:index'))
    return render(request, 'rides/login.html')


def register(request):
    return render(request, 'rides/register.html')


def register_request(request):
    try:
        #print("hahahhahaha")
        username_input = request.POST.get('user_name')
        password_input = request.POST.get('user_password')
        password_repeat_input = request.POST.get('user_password_repeat')

        # check for unique user name
        same_user = User.objects.filter(user_name__exact=username_input)
        if same_user != None:
            error_message = "This user name is taken, try another one!"
            return render(request, 'rides/register.html', {
                'error_message': error_message,
            })
        if password_input != password_repeat_input:
            error_message = "Password does not match the password repeat!"
            return render(request, 'rides/register.html', {
                'error_message': error_message,
            })
    except (KeyError):
        error_message = "Something went wrong..."
        return render(request, 'rides/register.html',
                      {error_message: error_message})
    else:
        new_user = User(user_name=username_input, user_password=password_input)
        new_user.save()
        return HttpResponseRedirect(reverse('rides:login'))
    #return HttpResponse("You're requesting for registration.")


# Create your views here.
