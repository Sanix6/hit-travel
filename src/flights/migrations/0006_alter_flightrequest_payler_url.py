# Generated by Django 5.0.2 on 2024-09-18 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0005_flightrequest_payler_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightrequest',
            name='payler_url',
            field=models.CharField(editable=False, max_length=700, null=True),
        ),
    ]
