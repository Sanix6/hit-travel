# Generated by Django 5.0.2 on 2024-12-05 07:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0057_requesthotel_adults_requesthotel_child_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="requesthotel",
            name="meal",
            field=models.CharField(blank=True, null=True, verbose_name="Питание"),
        ),
    ]
