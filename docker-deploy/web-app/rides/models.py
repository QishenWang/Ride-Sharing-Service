from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse

# Create your models here.


VEHICLE_TYPE = [("SEDAN", "SEDAN"), ("SUV", "SUV")]
MAX_PASSENGER_TYPE = [(1, "1 Passenger"), (2, "2 Passengers"),
                      (3, "3 Passengers"), (4, "4 Passengers"),
                      (5, "5 Passengers")]


class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=10,
                                    choices=VEHICLE_TYPE,
                                    default="SUV")
    plate_number = models.CharField(max_length=10)
    max_passenger_number = models.IntegerField(choices=MAX_PASSENGER_TYPE,
                                               default=5)
    special_vehicle_info = models.TextField(blank=True, default='')

    def __str__(self):
        return str(self.id) + '_' + self.plate_number


class Ride(models.Model):
    ride_owner = models.ForeignKey(User,
                                      related_name='Owner',
                                      on_delete=models.CASCADE)
    ride_driver = models.ForeignKey(User,
                                       related_name='Driver',
                                       on_delete=models.SET_NULL,
                                       null=True,
                                       blank=True
                                       )
    ride_sharer1 = models.ForeignKey(User,
                                        related_name='Sharer_1',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True
                                        )
    ride_sharer2 = models.ForeignKey(User,
                                        related_name='Sharer_2',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True
                                        )
    ride_sharer3 = models.ForeignKey(User,
                                        related_name='Sharer_3',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True
                                        )
    ride_sharer4 = models.ForeignKey(User,
                                        related_name='Sharer_4',
                                        on_delete=models.SET_NULL,
                                        null=True,
                                        blank=True)
    ride_destination = models.CharField(max_length=200)
    is_complete = models.BooleanField(default=False)
    is_sharable = models.BooleanField(default=False)
    arrival_time = models.DateTimeField(help_text='Format: 2022-02-14 12:00')
    passenger_number = models.IntegerField(default=1)
    vehicle_type = models.CharField(max_length=10,
                                    choices=VEHICLE_TYPE,
                                    default="SUV")
    special_request = models.TextField(blank=True, default='')

    def __str__(self):
        return str(self.id) + '_' + self.ride_owner.username + '_' + self.ride_destination
    def get_absolute_url(self):
        return reverse('rides:index')
