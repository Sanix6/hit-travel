# Generated by Django 5.0.2 on 2025-02-21 13:24

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CustomNotification",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="Заголовок"
                    ),
                ),
                ("text", models.TextField(max_length=400, verbose_name="Текст")),
                (
                    "all_users",
                    models.BooleanField(
                        default=False, verbose_name="Выбрать всех пользователей"
                    ),
                ),
                ("sent", models.BooleanField(default=False, editable=False)),
                (
                    "selected_users",
                    models.ManyToManyField(
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Выбрать пользователей",
                    ),
                ),
            ],
            options={
                "verbose_name": "Создать уведомление",
                "verbose_name_plural": "Создать уведомление",
            },
        ),
        migrations.CreateModel(
            name="TokenFCM",
            fields=[
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
                    "token",
                    models.CharField(max_length=256, unique=True, verbose_name="Токен"),
                ),
                (
                    "created_at",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата создания"
                    ),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="Дата обновления"),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fcm_token",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Токен",
                "verbose_name_plural": "Токены (Уведомление)",
            },
        ),
    ]
