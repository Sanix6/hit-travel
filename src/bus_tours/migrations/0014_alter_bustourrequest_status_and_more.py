# Generated by Django 4.2.4 on 2023-11-02 13:24

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bus_tours", "0013_bustourrequest_travelers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="bustourrequest",
            name="status",
            field=models.IntegerField(
                choices=[(1, "Новая"), (2, "В работе"), (3, "Подтверждена")],
                default=1,
                verbose_name="Статус",
            ),
        ),
        migrations.AlterField(
            model_name="bustourrequest",
            name="tour",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="bus_tour_request",
                to="bus_tours.bustours",
            ),
        ),
    ]
