from django.db import models

# Create your models here.
class User(models.Model):
    user_name = models.CharField(max_length=50)
    user_password = models.CharField(max_length=50)
    def __str__(self):
        return  str(self.id)+'_'+self.user_name

class Driver(models.Model):
    id = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True)
    vehicle_type = models.CharField(max_length=10)
    plate_number = models.CharField(max_length=10)
    max_passenger_number = models.IntegerField(default=5)



class Ride(models.Model):
    ride_owner_id = models.ForeignKey(User,related_name='Owner',on_delete=models.CASCADE)
    ride_driver_id = models.ForeignKey(Driver,related_name='Driver', on_delete=models.CASCADE)
    ride_sharer1_id = models.ForeignKey(User,related_name='Sharer_1', on_delete=models.CASCADE)
    ride_destination = models.CharField(max_length=200)
    is_complete = models.BooleanField(null=False)
    arrival_time = models.DateTimeField('requested date and time')
    passenger_number = models.IntegerField(default=1)
    vehicle_type = models.CharField(max_length=10)


