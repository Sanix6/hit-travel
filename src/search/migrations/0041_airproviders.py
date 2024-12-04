# Generated by Django 5.0.2 on 2024-05-29 19:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('search', '0040_flightrequest_paid'),
    ]

    operations = [
        migrations.CreateModel(
            name='AirProviders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=150, verbose_name='Код')),
                ('title', models.CharField(max_length=500, verbose_name='Название')),
                ('img', models.ImageField(upload_to='airlines', verbose_name='Логотип')),
            ],
            options={
                'verbose_name': 'Авиакомпания',
                'verbose_name_plural': 'Авиакомпании',
            },
        ),
    ]
