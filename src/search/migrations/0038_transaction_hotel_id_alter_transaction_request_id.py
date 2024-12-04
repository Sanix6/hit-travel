# Generated by Django 5.0.2 on 2024-05-13 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0037_alter_transaction_tour_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='hotel_id',
            field=models.IntegerField(blank=True, null=True, verbose_name='Айди отеля'),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='request_id',
            field=models.UUIDField(blank=True, null=True, verbose_name='Айди авиа'),
        ),
    ]