# Generated by Django 5.0.2 on 2024-03-16 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_requesthotel_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='requesthotel',
            name='status',
            field=models.IntegerField(choices=[(1, 'Новая заявка'), (2, 'В процессе покупки'), (3, 'Тур куплен'), (4, 'Отклонено')], default=2, verbose_name='Статус'),
        ),
    ]