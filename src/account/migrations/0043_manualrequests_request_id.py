# Generated by Django 5.0.2 on 2024-09-21 10:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0042_requesthotel_transaction_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="manualrequests",
            name="request_id",
            field=models.IntegerField(null=True),
        ),
    ]
