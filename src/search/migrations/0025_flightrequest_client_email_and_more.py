# Generated by Django 5.0.2 on 2024-04-21 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0024_alter_flightrequest_amount_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="flightrequest",
            name="client_email",
            field=models.CharField(
                blank=True, max_length=150, null=True, verbose_name="Почта клиента"
            ),
        ),
        migrations.AddField(
            model_name="flightrequest",
            name="client_phone",
            field=models.CharField(
                blank=True, max_length=150, null=True, verbose_name="Телефон клиента"
            ),
        ),
        migrations.AddField(
            model_name="flightrequest",
            name="payer_name",
            field=models.CharField(
                blank=True, max_length=150, null=True, verbose_name="Имя покупателя"
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="amount",
            field=models.FloatField(verbose_name="Сумма для платежа"),
        ),
    ]
