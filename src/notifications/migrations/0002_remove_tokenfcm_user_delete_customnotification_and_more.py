# Generated by Django 5.0.2 on 2025-02-25 07:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("notifications", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="tokenfcm",
            name="user",
        ),
        migrations.DeleteModel(
            name="CustomNotification",
        ),
        migrations.DeleteModel(
            name="TokenFCM",
        ),
    ]
