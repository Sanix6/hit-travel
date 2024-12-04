# Generated by Django 5.0.2 on 2024-04-21 21:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0023_rename_date_segments_date_from_segments_date_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightrequest',
            name='amount',
            field=models.FloatField(verbose_name='Сумма для платежа'),
        ),
        migrations.AlterField(
            model_name='flightrequest',
            name='billing_number',
            field=models.CharField(blank=True, default='123', max_length=500, null=True, verbose_name='Номер брони'),
        ),
        migrations.AlterField(
            model_name='flightrequest',
            name='status',
            field=models.CharField(choices=[('Ожидает оплаты', 'Ожидает оплаты'), ('Подтверждено', 'Подтверждено')], default='Ожидает оплаты', editable=False, max_length=255, verbose_name='Оплачено'),
        ),
    ]