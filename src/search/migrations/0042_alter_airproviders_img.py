# Generated by Django 5.0.2 on 2024-06-04 14:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0041_airproviders"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airproviders",
            name="img",
            field=models.ImageField(
                blank=True, null=True, upload_to="airlines", verbose_name="Логотип"
            ),
        ),
    ]
