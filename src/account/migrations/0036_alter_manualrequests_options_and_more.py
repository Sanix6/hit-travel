# Generated by Django 5.0.2 on 2024-09-18 18:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0035_remove_requesttourservice_a_flights_and_more"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="manualrequests",
            options={
                "verbose_name": "Ручные заявки",
                "verbose_name_plural": "Ручные заявки",
            },
        ),
        migrations.RemoveField(
            model_name="requesttour",
            name="from_main_view",
        ),
    ]
