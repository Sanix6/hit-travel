# Generated by Django 5.0.2 on 2024-07-18 09:11

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('notification', '0005_remove_usertoken_token_remove_usertoken_user_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='TokenFCM',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('token', models.CharField(max_length=256, unique=True, verbose_name='Токен')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
            ],
            options={
                'verbose_name': 'Токен',
                'verbose_name_plural': 'Токены (Уведомление)',
            },
        ),
        migrations.CreateModel(
            name='UserToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_active', models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')),
                ('token', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='users', to='notification.tokenfcm')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tokens', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Токен пользователя',
                'verbose_name_plural': 'Токены пользователей (Уведомление)',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='CustomNotification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=400, verbose_name='Текст')),
                ('all_users', models.BooleanField(default=False, verbose_name='Выбрать всех пользователей')),
                ('sent', models.BooleanField(default=False, editable=False)),
                ('selected_users', models.ManyToManyField(blank=True, to='notification.usertoken', verbose_name='Выбрать пользователей')),
            ],
            options={
                'verbose_name': 'Создать уведомление',
                'verbose_name_plural': 'Создать уведомление',
            },
        ),
    ]
