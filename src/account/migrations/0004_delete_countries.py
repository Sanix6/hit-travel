# Generated by Django 5.0.2 on 2024-02-12 13:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_countries_delete_filtercountries'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Countries',
        ),
    ]
