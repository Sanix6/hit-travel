# Generated by Django 5.0.2 on 2024-09-21 16:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0044_remove_manualrequests_data'),
    ]

    operations = [
        migrations.AddField(
            model_name='manualrequests',
            name='data',
            field=models.JSONField(default=dict, editable=False),
        ),
    ]