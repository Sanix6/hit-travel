# Generated by Django 5.0.2 on 2024-04-25 09:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0033_alter_flightrequest_billing_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='rid',
            field=models.CharField(editable=False, max_length=6, unique=True, verbose_name='Реквизит'),
        ),
    ]