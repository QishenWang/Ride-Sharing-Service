# Generated by Django 4.0.1 on 2022-01-20 19:13

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('rides', '0008_alter_user_user_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='driver',
            name='user_id',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='driver',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
        migrations.AlterField(
            model_name='ride',
            name='ride_owner_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='Owner', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ride',
            name='ride_sharer1_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Sharer_1', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ride',
            name='ride_sharer2_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Sharer_2', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ride',
            name='ride_sharer3_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Sharer_3', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='ride',
            name='ride_sharer4_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='Sharer_4', to=settings.AUTH_USER_MODEL),
        ),
        migrations.DeleteModel(
            name='User',
        ),
    ]