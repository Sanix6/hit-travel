# Generated by Django 5.0.2 on 2024-12-20 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flights', '0016_alter_airproviders_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='airproviders',
            name='code',
            field=models.CharField(max_length=150, unique=True, verbose_name='Код'),
        ),
    ]
