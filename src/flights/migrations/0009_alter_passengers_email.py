# Generated by Django 5.0.2 on 2024-11-27 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("flights", "0008_flightrequest_partner_affiliate_fee_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="passengers",
            name="email",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Эл-почта пассажира"
            ),
        ),
    ]
