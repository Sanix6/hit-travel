# Generated by Django 5.0.2 on 2024-07-03 05:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0028_remove_requesttourservices_extended_fields_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='requesttourservices',
            options={'verbose_name': 'Ручная заявка', 'verbose_name_plural': 'Ручные Заявки'},
        ),
    ]
