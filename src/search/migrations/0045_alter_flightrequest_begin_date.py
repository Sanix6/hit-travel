# Generated by Django 5.0.2 on 2024-07-18 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0044_flightrequest_begin_date_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flightrequest",
            name="begin_date",
            field=models.DateField(blank=True, null=True),
        ),
    ]
