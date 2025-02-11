# Generated by Django 5.0.2 on 2024-03-16 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0014_alter_traveler_passport_id"),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestHotel",
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
                    "hotelid",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Код отеля"
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Имя"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=100, null=True, verbose_name="Телефон"
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=100, null=True, verbose_name="E-mail"
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, null=True, verbose_name="Дата создания"
                    ),
                ),
            ],
            options={
                "verbose_name": "Заявка на отель",
                "verbose_name_plural": "Заявки на отели",
            },
        ),
    ]
