# Generated by Django 5.0.2 on 2024-09-20 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0039_alter_requesthotel_payler_url_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="passport_id",
            field=models.CharField(
                blank=True,
                max_length=36,
                null=True,
                unique=True,
                verbose_name="ID паспорт",
            ),
        ),
    ]
