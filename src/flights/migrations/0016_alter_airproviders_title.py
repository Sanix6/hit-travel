# Generated by Django 5.0.2 on 2024-12-20 12:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0015_alter_flightrequest_partner_affiliate_fee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airproviders",
            name="title",
            field=models.CharField(
                max_length=500, unique=True, verbose_name="Название"
            ),
        ),
    ]
