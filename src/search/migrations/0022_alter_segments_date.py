# Generated by Django 5.0.2 on 2024-04-20 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0021_segments_duration_hour_segments_duration_minute_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="segments",
            name="date",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="Дата вылета"
            ),
        ),
    ]
