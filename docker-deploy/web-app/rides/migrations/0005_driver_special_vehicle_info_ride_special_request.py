# Generated by Django 4.0.1 on 2022-01-16 21:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0004_ride_ride_sharer2_id_ride_ride_sharer3_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='special_vehicle_info',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='ride',
            name='special_request',
            field=models.TextField(null=True),
        ),
    ]
