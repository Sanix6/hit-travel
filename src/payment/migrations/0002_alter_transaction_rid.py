# Generated by Django 5.0.2 on 2024-08-05 06:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payment', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='rid',
            field=models.CharField(max_length=6, unique=True, verbose_name='Реквизит'),
        ),
    ]