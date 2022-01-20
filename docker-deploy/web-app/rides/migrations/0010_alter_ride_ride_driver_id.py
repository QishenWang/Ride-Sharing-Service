# Generated by Django 4.0.1 on 2022-01-20 19:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rides', '0009_driver_user_id_alter_driver_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='ride_driver_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Driver', to=settings.AUTH_USER_MODEL),
        ),
    ]
