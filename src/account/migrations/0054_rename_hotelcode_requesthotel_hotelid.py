# Generated by Django 5.0.2 on 2024-12-05 06:26

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0053_rename_hotelid_requesthotel_hotelcode"),
    ]

    operations = [
        migrations.RenameField(
            model_name="requesthotel",
            old_name="hotelcode",
            new_name="hotelid",
        ),
    ]
