# Generated by Django 5.0.2 on 2024-08-05 06:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0002_alter_transaction_rid'),
        ('search', '0045_alter_flightrequest_begin_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='flightcancel',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='payment.transaction', verbose_name='Транзакция'),
        ),
    ]
