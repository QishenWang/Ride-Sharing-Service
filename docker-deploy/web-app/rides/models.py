from django.db import models

# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length=50)
    user_password = models.CharField(max_length=50)

    def __str__(self):
        return  str(self.id)+'_'+self.user_name

VEHICLE_TYPE = [("SEDAN", "SEDAN"), ("SUV", "SUV")]
MAX_PASSENGER_TYPE = [(1, "1 Passenger"), (2, "2 Passengers"), (3, "3 Passengers"), (4, "4 Passengers"), (5, "5 Passengers")]

class Driver(models.Model):
    id = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE, default="SUV")
    plate_number = models.CharField(max_length=10)
    max_passenger_number = models.IntegerField(choices=MAX_PASSENGER_TYPE, default=5)
    special_vehicle_info = models.TextField(blank=True, default='')

    def __str__(self):
        return str(self.id) + '_' + self.plate_number


class Ride(models.Model):
    ride_owner_id = models.ForeignKey(User, related_name='Owner', on_delete=models.CASCADE)
    ride_driver_id = models.ForeignKey(Driver, related_name='Driver', on_delete=models.CASCADE, null=True)
    ride_sharer1_id = models.ForeignKey(User, related_name='Sharer_1', on_delete=models.CASCADE, null=True)
    ride_sharer2_id = models.ForeignKey(User, related_name='Sharer_2', on_delete=models.CASCADE, null=True)
    ride_sharer3_id = models.ForeignKey(User, related_name='Sharer_3', on_delete=models.CASCADE, null=True)
    ride_sharer4_id = models.ForeignKey(User, related_name='Sharer_4', on_delete=models.CASCADE, null=True)
    ride_destination = models.CharField(max_length=200)
    is_complete = models.BooleanField(default=False)
    is_sharable = models.BooleanField(default=False)
    arrival_time = models.DateTimeField('requested date and time')
    passenger_number = models.IntegerField(default=1)
    vehicle_type = models.CharField(max_length=10, choices=VEHICLE_TYPE, default="SUV")
    special_request = models.TextField(blank=True, default='')

    def __str__(self):
        return str(self.id) + '_' + self.ride_owner_id


