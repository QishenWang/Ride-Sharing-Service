# Generated by Django 4.0.1 on 2022-01-23 20:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0015_alter_ride_arrival_time_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='ride',
            name='check_arrival_time_gt_now',
        ),
    ]
