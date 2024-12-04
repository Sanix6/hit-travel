# Generated by Django 5.0.2 on 2024-07-17 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0043_alter_airports_code_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='flightrequest',
            name='begin_date',
            field=models.DateField(blank=True, editable=False, null=True),
        ),
        migrations.AddField(
            model_name='flightrequest',
            name='sent_notification',
            field=models.BooleanField(default=False, editable=False),
        ),
    ]