# Generated by Django 5.0.2 on 2024-11-28 13:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0046_requesthotel_pdf_requesttour_pdf"),
    ]

    operations = [
        migrations.AddField(
            model_name="traveler",
            name="hotel",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="traveler",
                to="account.requesthotel",
            ),
        ),
    ]
