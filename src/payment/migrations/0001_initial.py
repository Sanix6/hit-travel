# Generated by Django 5.0.2 on 2024-08-03 07:54

import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "rid",
                    models.CharField(
                        editable=False,
                        max_length=6,
                        unique=True,
                        verbose_name="Реквизит",
                    ),
                ),
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "qid",
                    models.CharField(
                        blank=True, max_length=450, null=True, verbose_name="QID"
                    ),
                ),
                (
                    "status",
                    models.CharField(
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
                (
                    "name",
                    models.CharField(
                        choices=[
                            ("tour", "Тур"),
                            ("hotel", "Отель"),
                            ("ticket", "Авиабилет"),
                        ],
                        max_length=255,
                        verbose_name="Платёж для",
                    ),
                ),
                (
                    "request_id",
                    models.UUIDField(blank=True, null=True, verbose_name="Айди авиа"),
                ),
                (
                    "tour_id",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Айди тура"
                    ),
                ),
                (
                    "hotel_id",
                    models.IntegerField(
                        blank=True, null=True, verbose_name="Айди отеля"
                    ),
                ),
                ("amount", models.FloatField(verbose_name="Сумма для платежа")),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="payment_transactions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Платеж",
                "verbose_name_plural": "Платежы",
            },
        ),
    ]
