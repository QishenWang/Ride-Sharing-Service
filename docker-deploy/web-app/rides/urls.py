from django.urls import path

from . import views

app_name = 'rides'
urlpatterns = [
    #path('', views.index, name='index'),
    #path('login/', views.login, name='login'),
    path('', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('register_request/', views.register_request, name='register_request'),
]