# Generated by Django 4.2.4 on 2023-12-03 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("webhooks", "0003_createclient"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="createclient",
            options={
                "verbose_name": "Клиент CRM",
                "verbose_name_plural": "Клиенты CRM",
            },
        ),
    ]
