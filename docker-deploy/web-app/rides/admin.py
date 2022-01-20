from django.contrib import admin

# Register your models here.
from .models import  Driver, Ride
from django.contrib.auth.models import User

#admin.site.unregister(User)
#admin.site.register(User)
admin.site.register(Driver)
admin.site.register(Ride)
