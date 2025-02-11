# Generated by Django 5.0.2 on 2024-07-17 12:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0032_delete_tourist"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="gender",
            field=models.CharField(
                choices=[("м", "Муж"), ("ж", "Жен"), ("н", "Неизвестно")],
                max_length=3,
                verbose_name="Пол",
            ),
        ),
    ]
