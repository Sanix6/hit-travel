# Generated by Django 5.0.2 on 2024-04-18 19:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0011_flightrequest_passengers_segments_transaction"),
    ]

    operations = [
        migrations.AddField(
            model_name="flightrequest",
            name="amount",
            field=models.FloatField(default=1, verbose_name="Сумма"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="flightrequest",
            name="billing_number",
            field=models.CharField(
                default=1, max_length=500, verbose_name="Номер брони"
            ),
            preserve_default=False,
        ),
    ]
