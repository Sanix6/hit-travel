# Generated by Django 5.0.2 on 2024-07-09 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('notification', '0002_alter_tokenfcm_options_alter_usertoken_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Дата изменения'),
        ),
    ]
