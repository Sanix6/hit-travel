# Generated by Django 5.0.2 on 2024-02-12 14:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_delete_countries'),
    ]

    operations = [
        migrations.AddField(
            model_name='traveler',
            name='authority',
            field=models.CharField(default=0, max_length=100, verbose_name='Кем выдан'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='traveler',
            name='inn',
            field=models.CharField(default=0, max_length=100, verbose_name='ИНН'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='traveler',
            name='passport_id',
            field=models.CharField(default=0, max_length=100, verbose_name='Айди паспорта'),
            preserve_default=False,
        ),
    ]