# Generated by Django 4.2.4 on 2023-10-28 10:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bus_tours', '0008_reviews_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='bustours',
            name='departure',
            field=models.CharField(choices=[('Ташкент', 'Ташкент'), ('Бишкек', 'Бишкек'), ('Баку', 'Баку')], default='Бишкек', max_length=255, verbose_name='Откуда'),
        ),
        migrations.AddField(
            model_name='bustours',
            name='num_of_tourists',
            field=models.IntegerField(default=2, verbose_name='Количество туристов'),
        ),
    ]
