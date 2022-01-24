from django.urls import path

from . import views
from django.contrib.auth import views as auth_views
from .views import (RideListView, RideCreateView, RideUpdateView,
                    DriverConfirmedListView, DriverConfirmedDetailView)

app_name = 'rides'
urlpatterns = [
    path('', RideListView.as_view(), name='index'),
    path('register/', views.register, name='register'),
    path('login/',
         auth_views.LoginView.as_view(template_name='rides/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='rides/logout.html'),
         name='logout'),
    path('newdriver/', views.newdriver, name='newdriver'),
    path('newride/', RideCreateView.as_view(), name='newride'),
    path('<int:pk>/updateride/', RideUpdateView.as_view(), name='updateride'),
    path('driver/', DriverConfirmedListView.as_view(), name='driver'),
    path('<int:pk>/driver_ride_detail/',
         DriverConfirmedDetailView.as_view(),
         name='driver_ride_detail'),
]