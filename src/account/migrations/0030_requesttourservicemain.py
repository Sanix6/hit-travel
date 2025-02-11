# Generated by Django 5.0.2 on 2024-07-04 07:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("account", "0029_alter_requesttourservices_options"),
    ]

    operations = [
        migrations.CreateModel(
            name="RequestTourServiceMain",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "tour_name",
                    models.CharField(
                        blank=True, default="Пакетный тур", max_length=150, null=True
                    ),
                ),
                (
                    "manager_name",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                (
                    "office_name",
                    models.CharField(blank=True, max_length=250, null=True),
                ),
                ("date_begin", models.CharField(blank=True, max_length=50, null=True)),
                ("date_end", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "status_pay_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "payment_deadline_client",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "company_name",
                    models.CharField(
                        blank=True, default="Hit Travel", max_length=150, null=True
                    ),
                ),
                (
                    "client_requirements_country_names",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "t_service_type",
                    models.CharField(
                        blank=True, default="Пакетный тур", max_length=400, null=True
                    ),
                ),
                (
                    "t_partner_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "t_date_begin",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("t_date_end", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "t_price_netto",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                ("t_currency", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "t_tourists_count",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "t_tourists_child_count",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "t_tourists_baby_count",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "t_hotel_place_id",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "t_hotel_place",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "h_service_type",
                    models.CharField(
                        blank=True, default="Отель", max_length=400, null=True
                    ),
                ),
                (
                    "h_date_begin",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("h_date_end", models.CharField(blank=True, max_length=50, null=True)),
                ("h_hotel", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "h_hotel_place_id",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "h_hotel_place",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                (
                    "i_service_type",
                    models.CharField(
                        blank=True, default="Страховка", max_length=400, null=True
                    ),
                ),
                (
                    "i_partner_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "i_date_begin",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("i_date_end", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "i_price_netto",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                ("i_currency", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "tr_service_type",
                    models.CharField(
                        blank=True, default="Трансфер", max_length=400, null=True
                    ),
                ),
                (
                    "tr_partner_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                (
                    "tr_date_begin",
                    models.CharField(blank=True, max_length=50, null=True),
                ),
                ("tr_date_end", models.CharField(blank=True, max_length=50, null=True)),
                ("tr_course", models.CharField(blank=True, max_length=500, null=True)),
                (
                    "tr_price_netto",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                ("tr_currency", models.CharField(blank=True, max_length=50, null=True)),
                (
                    "a_main",
                    models.CharField(
                        blank=True, default="Авиабилет", max_length=400, null=True
                    ),
                ),
                ("a_description", models.TextField(blank=True, null=True)),
                (
                    "a_partner_name",
                    models.CharField(blank=True, max_length=150, null=True),
                ),
                ("have_tour", models.BooleanField(default=False)),
                ("have_hotel", models.BooleanField(default=False)),
                ("have_insurance", models.BooleanField(default=False)),
                ("have_transfer", models.BooleanField(default=False)),
                ("have_avia", models.BooleanField(default=False)),
                ("a_flights", models.ManyToManyField(blank=True, to="account.flight")),
                (
                    "main",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="account.requesttour",
                    ),
                ),
            ],
        ),
    ]
