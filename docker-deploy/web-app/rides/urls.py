from django.urls import path

from . import views
from django.contrib.auth import views as auth_views

app_name = 'rides'
urlpatterns = [
    path('', views.index, name='index'),
    #path('login/', views.login, name='login'),
    #path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    #path('logout/', views.logout, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='rides/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='rides/logout.html'), name='logout'),
]