# Generated by Django 4.2.4 on 2023-10-27 11:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Meals",
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
                ("name", models.CharField(max_length=5)),
                ("fullname", models.CharField(max_length=255)),
                ("russian", models.CharField(max_length=255)),
                ("russianfull", models.CharField(max_length=255)),
            ],
        ),
    ]
