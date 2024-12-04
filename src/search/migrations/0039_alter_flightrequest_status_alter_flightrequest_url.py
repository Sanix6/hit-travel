# Generated by Django 5.0.2 on 2024-05-16 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0038_transaction_hotel_id_alter_transaction_request_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightrequest',
            name='status',
            field=models.CharField(choices=[('booked', 'Бронирование'), ('ticketed', 'Оплачено'), ('canceled', 'Отменено'), ('timeout', 'Истек срок оплаты')], default='booked', max_length=255, verbose_name='Статус'),
        ),
        migrations.AlterField(
            model_name='flightrequest',
            name='url',
            field=models.TextField(editable=False),
        ),
    ]
