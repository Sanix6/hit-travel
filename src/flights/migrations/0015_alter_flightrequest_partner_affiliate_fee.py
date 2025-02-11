# Generated by Django 5.0.2 on 2024-12-05 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0014_flightrequest_partner_affiliate_fee"),
    ]

    operations = [
        migrations.AlterField(
            model_name="flightrequest",
            name="partner_affiliate_fee",
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=10,
                null=True,
                verbose_name="Комиссия партнера",
            ),
        ),
    ]
