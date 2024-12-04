# Generated by Django 5.0.2 on 2024-08-09 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_tours', '0017_alter_bustours_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bustourrequest',
            name='issued_by',
            field=models.CharField(max_length=100, verbose_name='Орган выдачи'),
        ),
        migrations.AlterField(
            model_name='cities',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название города'),
        ),
    ]
