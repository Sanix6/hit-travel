# Generated by Django 5.0.2 on 2024-05-10 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_alter_requesthotel_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='passport_id',
            field=models.CharField(blank=True, max_length=8, null=True, unique=True, verbose_name='ID паспорт'),
        ),
    ]