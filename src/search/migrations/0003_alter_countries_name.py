# Generated by Django 5.0.2 on 2024-02-12 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0002_countries"),
    ]

    operations = [
        migrations.AlterField(
            model_name="countries",
            name="name",
            field=models.CharField(
                editable=False, max_length=200, verbose_name="Страна"
            ),
        ),
    ]
