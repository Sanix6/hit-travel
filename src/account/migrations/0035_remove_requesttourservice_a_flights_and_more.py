# Generated by Django 5.0.2 on 2024-09-18 18:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        (
            "account",
            "0034_alter_payments_bank_name_alter_requesttour_issued_by_and_more",
        ),
    ]

    operations = [
        migrations.RemoveField(
            model_name="requesttourservice",
            name="a_flights",
        ),
        migrations.RemoveField(
            model_name="requesttourservice",
            name="main",
        ),
        migrations.CreateModel(
            name="ManualRequests",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("data", models.JSONField(default=dict)),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Клиент",
                    ),
                ),
            ],
        ),
        migrations.DeleteModel(
            name="Flight",
        ),
        migrations.DeleteModel(
            name="RequestTourService",
        ),
    ]
