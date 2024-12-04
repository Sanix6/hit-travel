# Generated by Django 5.0.2 on 2024-04-20 09:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0020_alter_flightrequest_status_alter_flightrequest_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='segments',
            name='duration_hour',
            field=models.IntegerField(blank=True, help_text='В пути', null=True, verbose_name='Час'),
        ),
        migrations.AddField(
            model_name='segments',
            name='duration_minute',
            field=models.IntegerField(blank=True, help_text='В пути', null=True, verbose_name='Минут'),
        ),
        migrations.AddField(
            model_name='segments',
            name='time_from',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Время вылета'),
        ),
        migrations.AddField(
            model_name='segments',
            name='time_to',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='Время прилета'),
        ),
        migrations.AlterField(
            model_name='segments',
            name='date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата вылета'),
        ),
    ]
