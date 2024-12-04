# Generated by Django 5.0.2 on 2024-12-01 05:06

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0051_remove_traveler_hotel_hoteltraveler'),
    ]

    operations = [
        migrations.AlterField(
            model_name='hoteltraveler',
            name='hotel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='travelers', to='account.requesthotel'),
        ),
    ]
