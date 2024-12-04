# Generated by Django 5.0.2 on 2024-08-07 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0047_delete_transaction'),
    ]

    operations = [
        migrations.DeleteModel(
            name='AirProviders',
        ),
        migrations.RemoveField(
            model_name='flightrequest',
            name='user',
        ),
        migrations.RemoveField(
            model_name='segments',
            name='main',
        ),
        migrations.RemoveField(
            model_name='passengers',
            name='main',
        ),
        migrations.DeleteModel(
            name='FlightCancel',
        ),
        migrations.DeleteModel(
            name='Segments',
        ),
        migrations.DeleteModel(
            name='FlightRequest',
        ),
        migrations.DeleteModel(
            name='Passengers',
        ),
    ]
