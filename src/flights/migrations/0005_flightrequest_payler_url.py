# Generated by Django 5.0.2 on 2024-09-18 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0004_alter_aviaagreement_options"),
    ]

    operations = [
        migrations.AddField(
            model_name="flightrequest",
            name="payler_url",
            field=models.CharField(max_length=700, null=True),
        ),
    ]
