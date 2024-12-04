# Generated by Django 5.0.2 on 2024-08-09 16:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0033_alter_user_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payments',
            name='bank_name',
            field=models.CharField(blank=True, max_length=400, null=True, verbose_name='Название банка'),
        ),
        migrations.AlterField(
            model_name='requesttour',
            name='issued_by',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Орган выдачи'),
        ),
        migrations.AlterField(
            model_name='traveler',
            name='issued_by',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Орган, выдачи з/п'),
        ),
        migrations.AlterField(
            model_name='user',
            name='issued_by',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Орган выдачи'),
        ),
    ]
