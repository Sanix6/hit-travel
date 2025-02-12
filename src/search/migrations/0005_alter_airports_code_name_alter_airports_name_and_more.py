# Generated by Django 5.0.2 on 2024-04-06 09:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0004_countries_code_name_cities_airports"),
    ]

    operations = [
        migrations.AlterField(
            model_name="airports",
            name="code_name",
            field=models.CharField(
                default=123, help_text="FRU", max_length=3, verbose_name="Код аэропорта"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="airports",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Аэропрт"),
        ),
        migrations.AlterField(
            model_name="cities",
            name="code_name",
            field=models.CharField(
                default=123, help_text="FRU", max_length=3, verbose_name="Код города"
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="cities",
            name="main",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="cities",
                to="search.countries",
                verbose_name="Страна",
            ),
        ),
        migrations.AlterField(
            model_name="cities",
            name="name",
            field=models.CharField(max_length=200, verbose_name="Город"),
        ),
    ]
