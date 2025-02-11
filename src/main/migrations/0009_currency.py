# Generated by Django 4.2.4 on 2024-01-15 08:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("main", "0008_alter_versions_options_alter_versions_appstore_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Currency",
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
                (
                    "currency",
                    models.CharField(
                        choices=[("USD", "USD"), ("EUR", "EUR")],
                        max_length=20,
                        unique=True,
                        verbose_name="Валюта",
                    ),
                ),
                (
                    "purchase",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Покупка"
                    ),
                ),
                (
                    "sell",
                    models.DecimalField(
                        decimal_places=2, max_digits=10, verbose_name="Продажа"
                    ),
                ),
            ],
            options={
                "verbose_name": "Курс",
                "verbose_name_plural": "Курсы",
            },
        ),
    ]
