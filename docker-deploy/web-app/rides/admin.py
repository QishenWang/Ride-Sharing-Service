from django.contrib import admin

# Register your models here.
from .models import  Driver, Ride, ShareRecord
from django.contrib.auth.models import User

admin.site.register(Driver)
admin.site.register(Ride)
admin.site.register(ShareRecord)
