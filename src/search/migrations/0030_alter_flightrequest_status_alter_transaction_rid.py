# Generated by Django 5.0.2 on 2024-04-22 09:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0029_transaction'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightrequest',
            name='status',
            field=models.CharField(choices=[('pending', 'Ожидает оплаты'), ('confirm', 'Подтверждено'), ('canceled', 'Отменено')], default='pending', max_length=255, verbose_name='Оплачено'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='rid',
            field=models.CharField(default='871687', editable=False, max_length=6, unique=True, verbose_name='Уникальный код'),
        ),
    ]
