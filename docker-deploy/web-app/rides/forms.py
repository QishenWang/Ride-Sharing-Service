from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Driver, Ride


class RegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User  #The model this form interact with
        fields = ['username', 'email', 'password1',
                  'password2']  #The fields and order of fields that are shown


class DriverProfileForm(forms.ModelForm):

    class Meta:
        model = Driver
        fields = [
            'vehicle_type', 'plate_number', 'max_passenger_number',
            'special_vehicle_info'
        ]
