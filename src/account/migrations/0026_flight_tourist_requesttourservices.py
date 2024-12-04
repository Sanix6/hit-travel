# Generated by Django 5.0.2 on 2024-07-03 03:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0025_requesttour_from_main_view'),
    ]

    operations = [
        migrations.CreateModel(
            name='Flight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_begin', models.DateTimeField(blank=True, null=True)),
                ('time_begin', models.TimeField(blank=True, null=True)),
                ('date_end', models.DateTimeField(blank=True, null=True)),
                ('time_end', models.TimeField(blank=True, null=True)),
                ('flight_number', models.CharField(blank=True, max_length=50, null=True)),
                ('course_begin', models.CharField(blank=True, max_length=255, null=True)),
                ('course_end', models.CharField(blank=True, max_length=255, null=True)),
                ('terminal_begin', models.CharField(blank=True, max_length=50, null=True)),
                ('terminal_end', models.CharField(blank=True, max_length=50, null=True)),
                ('code_begin', models.CharField(blank=True, max_length=10, null=True)),
                ('code_end', models.CharField(blank=True, max_length=10, null=True)),
                ('seats', models.CharField(blank=True, max_length=50, null=True)),
                ('tickets', models.CharField(blank=True, max_length=50, null=True)),
                ('type', models.CharField(blank=True, max_length=50, null=True)),
                ('flight_class', models.CharField(blank=True, max_length=50, null=True)),
                ('duration', models.CharField(blank=True, max_length=50, null=True)),
                ('baggage', models.CharField(blank=True, max_length=50, null=True)),
                ('supplier_id', models.IntegerField(blank=True, null=True)),
                ('supplier_name', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tourist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tourist_id', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='RequestTourServices',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('date_begin', models.DateTimeField(blank=True, null=True)),
                ('date_end', models.DateTimeField(blank=True, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('in_package', models.BooleanField(blank=True, default=False, null=True)),
                ('course', models.CharField(blank=True, max_length=255, null=True)),
                ('duration', models.CharField(blank=True, max_length=255, null=True)),
                ('cb_price_netto_operator', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('price_netto', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rate_netto', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('currency_id_netto', models.IntegerField(blank=True, null=True)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('rate', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('currency_id', models.IntegerField(blank=True, null=True)),
                ('discount', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=10, null=True)),
                ('discount_in_percent', models.DecimalField(blank=True, decimal_places=2, default=0, max_digits=5, null=True)),
                ('tourists_count', models.IntegerField(blank=True, null=True)),
                ('tourists_child_count', models.IntegerField(blank=True, null=True)),
                ('tourists_baby_count', models.IntegerField(blank=True, null=True)),
                ('internet_link', models.URLField(blank=True, null=True)),
                ('is_active', models.BooleanField(blank=True, default=True, null=True)),
                ('catalog_package_id', models.IntegerField(blank=True, default=0, null=True)),
                ('catalog_service_id', models.IntegerField(blank=True, default=0, null=True)),
                ('catalog_quota_count', models.IntegerField(blank=True, default=0, null=True)),
                ('service_type', models.CharField(blank=True, max_length=255, null=True)),
                ('service_type_id', models.IntegerField(blank=True, null=True)),
                ('partner_id', models.IntegerField(blank=True, null=True)),
                ('partner_name', models.CharField(blank=True, max_length=255, null=True)),
                ('partner_name_en', models.CharField(blank=True, max_length=255, null=True)),
                ('partner_inn', models.CharField(blank=True, max_length=255, null=True)),
                ('country_id', models.IntegerField(blank=True, null=True)),
                ('country', models.CharField(blank=True, max_length=255, null=True)),
                ('country_en', models.CharField(blank=True, max_length=255, null=True)),
                ('city_id', models.IntegerField(blank=True, null=True)),
                ('city', models.CharField(blank=True, max_length=255, null=True)),
                ('city_en', models.CharField(blank=True, max_length=255, null=True)),
                ('hotel_id', models.IntegerField(blank=True, null=True)),
                ('hotel', models.CharField(blank=True, max_length=255, null=True)),
                ('hotel_en', models.CharField(blank=True, max_length=255, null=True)),
                ('hotel_type_id', models.IntegerField(blank=True, null=True)),
                ('hotel_type', models.CharField(blank=True, max_length=255, null=True)),
                ('hotel_type_en', models.CharField(blank=True, max_length=255, null=True)),
                ('hotel_place_id', models.IntegerField(blank=True, null=True)),
                ('hotel_place', models.CharField(blank=True, max_length=255, null=True)),
                ('nutrition_id', models.IntegerField(blank=True, null=True)),
                ('nutrition', models.CharField(blank=True, max_length=255, null=True)),
                ('nutrition_en', models.CharField(blank=True, max_length=255, null=True)),
                ('currency_netto', models.CharField(blank=True, max_length=255, null=True)),
                ('currency_code_netto', models.CharField(blank=True, max_length=3, null=True)),
                ('currency', models.CharField(blank=True, max_length=255, null=True)),
                ('currency_code', models.CharField(blank=True, max_length=3, null=True)),
                ('extended_fields', models.JSONField(blank=True, null=True)),
                ('flights', models.ManyToManyField(blank=True, to='account.flight')),
                ('main', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='account.requesttour')),
                ('tourists', models.ManyToManyField(blank=True, to='account.tourist')),
            ],
        ),
    ]
