# Generated by Django 5.0.2 on 2024-04-22 09:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("search", "0031_alter_transaction_rid"),
    ]

    operations = [
        migrations.AddField(
            model_name="transaction",
            name="qid",
            field=models.CharField(
                blank=True, max_length=450, null=True, verbose_name="QID"
            ),
        ),
        migrations.AlterField(
            model_name="transaction",
            name="rid",
            field=models.CharField(
                default="192035",
                editable=False,
                max_length=6,
                unique=True,
                verbose_name="Уникальный код",
            ),
        ),
    ]
