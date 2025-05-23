# Generated by Django 5.0.2 on 2024-05-10 10:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0035_flightcancel"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="tour_id",
            field=models.IntegerField(
                blank=True, max_length=150, null=True, verbose_name="Айди тура"
            ),
        ),
        migrations.AlterField(
            model_name="flightcancel",
            name="flight",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="search.flightrequest",
                verbose_name="Билет",
            ),
        ),
        migrations.AlterField(
            model_name="flightcancel",
            name="transaction",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="search.transaction",
                verbose_name="Транзакция",
            ),
        ),
        migrations.AlterField(
            model_name="flightrequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Ожидает оплаты"),
                    ("confirm", "Подтверждено"),
                    ("canceled", "Отменено"),
                    ("timeout", "Истек срок оплаты"),
                ],
                default="pending",
                max_length=255,
                verbose_name="Оплачено",
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="status",
            field=models.CharField(
                choices=[
                    ("processing", "В обработке"),
                    ("completed", "Успешно завершено"),
                    ("canceled", "Отменен"),
                    ("timeout", "Истек срок оплаты"),
                ],
                max_length=255,
                verbose_name="Статус",
            ),
        ),
    ]
