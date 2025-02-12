# Generated by Django 5.0.2 on 2024-02-15 13:11

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0006_remove_traveler_authority_traveler_country_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="requesttour",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"Managers": "Менеджеры"},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="requested_tours",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
