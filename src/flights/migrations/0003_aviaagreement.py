# Generated by Django 5.0.2 on 2024-09-05 12:12

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0002_airproviders'),
    ]

    operations = [
        migrations.CreateModel(
            name='AviaAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('agreement', ckeditor.fields.RichTextField()),
            ],
        ),
    ]
