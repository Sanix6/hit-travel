# Generated by Django 5.0.2 on 2024-02-17 09:23

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0009_user_whatsapp_alter_requesttour_manager"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="traveler",
            name="country",
        ),
        migrations.RemoveField(
            model_name="traveler",
            name="date_of_issue",
        ),
        migrations.RemoveField(
            model_name="traveler",
            name="gender",
        ),
        migrations.RemoveField(
            model_name="traveler",
            name="passport_id",
        ),
        migrations.RemoveField(
            model_name="traveler",
            name="validity",
        ),
        migrations.AlterField(
            model_name="requesttour",
            name="manager",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"groups__name": "Managers"},
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="tour_manager",
                to=settings.AUTH_USER_MODEL,
                verbose_name="Менеджер",
            ),
        ),
        migrations.AlterField(
            model_name="traveler",
            name="first_name",
            field=models.CharField(
                max_length=100, verbose_name="Имя по загранпаспорту"
            ),
        ),
        migrations.AlterField(
            model_name="traveler",
            name="inn",
            field=models.CharField(
                blank=True, max_length=100, null=True, verbose_name="Серия и номер"
            ),
        ),
        migrations.AlterField(
            model_name="traveler",
            name="issued_by",
            field=models.CharField(
                blank=True, null=True, verbose_name="Орган, выдачи з/п"
            ),
        ),
        migrations.AlterField(
            model_name="traveler",
            name="last_name",
            field=models.CharField(
                max_length=100, verbose_name="Фамилия по загранпаспорту"
            ),
        ),
    ]
