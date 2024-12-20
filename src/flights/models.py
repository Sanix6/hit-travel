from django.db import models
from django.utils.translation import gettext_lazy as _
from src.account.models import User
from django.core.validators import URLValidator
from ckeditor.fields import RichTextField
from .choices import *
from src.payment import models as payment_model
import uuid
import random

class AviaAgreement(models.Model):
    agreement = RichTextField()

    class Meta:
        verbose_name = "Политика соглашения об авиабилетах"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"Политика соглашения об авиабилетах"

class AirProviders(models.Model):
    code = models.CharField(_("Код"), max_length=150, unique=True)
    title = models.CharField(_("Название"), max_length=500, unique=True)
    img = models.ImageField(_("Логотип"), upload_to="airlines", blank=True, null=True)

    class Meta:
        verbose_name = "Авиакомпания"
        verbose_name_plural = "Авиакомпании"


class FlightRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    # url = models.TextField(validators=[URLValidator()])
    url = models.TextField(editable=False)
    status = models.CharField(_("Статус"), choices=BOOK_STATUS, max_length=255, default="booked", editable=True)
    user = models.ForeignKey(User, verbose_name=_("Пользователь"), on_delete=models.CASCADE, related_name="flight_requests")
    client_email = models.CharField(_("Почта клиента"), max_length=150, blank=True, null=True)
    client_phone = models.CharField(_("Телефон клиента"), max_length=150, blank=True, null=True)
    payer_name = models.CharField(_("Имя покупателя"), max_length=150, blank=True, null=True)
    billing_number = models.CharField(_("Номер брони"), max_length=500, blank=True, null=True)
    amount = models.FloatField(_("Сумма для платежа"))
    paid = models.FloatField(_("Всего оплачено"), blank=True, null=True)
    book_class = models.CharField(_("Класс"), choices=BOOK_CLASS_CHOICE, max_length=250)
    partner_affiliate_fee = models.DecimalField(_("Комиссия партнера"), max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)
    sent_notification = models.BooleanField(default=False, editable=False)
    begin_date = models.DateField(editable=True, blank=True, null=True)
    payler_url = models.CharField(max_length=700, null=True, editable=False)
    transaction_id = models.CharField(max_length=700, null=True, editable=False)
    type = models.CharField(max_length=255, null=True, blank=True)
    is_baggage = models.BooleanField(default=True)
    provider = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, null=True, blank=True)
    flight_number = models.IntegerField(null=True, blank=True)
    adt = models.IntegerField(null=True, blank=True)
    chd = models.IntegerField(null=True, blank=True)
    inf = models.IntegerField(null=True, blank=True)



    class Meta:
        verbose_name = 'Заявки на авиабилеты'
        verbose_name_plural = 'Заявки на авиабилеты'


    def __str__(self):
        return f"{self.payer_name} - {self.client_phone}"
    

class Passengers(models.Model):
    main = models.ForeignKey(FlightRequest, on_delete=models.CASCADE, related_name="passengers")
    first_name = models.CharField(_("Имя"), max_length=150, blank=True, null=True)
    last_name = models.CharField(_("Фамилия"), max_length=150, blank=True, null=True)
    middlename = models.CharField(_("Отчество"), max_length=150, blank=True, null=True)
    age = models.CharField(_("Тип возраста"), choices=PASSENGER_TYPE, max_length=150, blank=True, null=True)
    birthdate = models.DateField(_("Дата рождения"), blank=True, null=True)
    doctype = models.CharField(_("Тип документа"), choices=DOCUMENT_TYPE, max_length=5, blank=True, null=True)
    docnum = models.CharField(_("Номер документа"), max_length=50, help_text="Серия и номер", blank=True, null=True)
    docexp = models.DateField(_("Действует до"), blank=True, null=True)
    gender = models.CharField(_("Пол"), choices=PASSENGER_GENDER, max_length=5, blank=True, null=True)
    citizen = models.CharField(_("Код страны"), max_length=5, help_text="код страны в формате ISO 3166-1 alpha-2",blank=True, null=True)
    phone = models.CharField(_("Телефон номер пассажира"), max_length=100, blank=True, null=True)
    email = models.CharField(_("Эл-почта пассажира"), max_length=100, blank=True, null=True)


    class Meta:
        verbose_name = 'Пассажир'
        verbose_name_plural = 'Пассажир'


class Segments(models.Model):
    main = models.ForeignKey(FlightRequest, on_delete=models.CASCADE, related_name="segments")

    from_name = models.CharField(_("Откуда (город)"), help_text="Алматы", max_length=150)
    from_iata = models.CharField(_("Код города"), help_text="ALA", max_length=150)
    from_country = models.CharField(_("Страна отправления"), help_text="Казахстан", max_length=150)

    to_name = models.CharField(_("Куда (город)"), help_text="Бишкек", max_length=150)
    to_iata = models.CharField(_("Код города"), help_text="FRU", max_length=150)
    to_country = models.CharField(_("Страна прибытие"), help_text="Кыргызстан", max_length=150)

    date_from = models.CharField(_("Дата вылета"), max_length=20, blank=True, null=True)
    date_to = models.CharField(_("Дата прилета"), max_length=20, blank=True, null=True)
    time_from = models.CharField(_("Время вылета"), max_length=20, blank=True, null=True)
    time_to = models.CharField(_("Время прилета"), max_length=20, blank=True, null=True)
    duration_hour = models.IntegerField(_("Час"), help_text=_("В пути"), blank=True, null=True)
    duration_minute = models.IntegerField(_("Минут"), help_text=_("В пути"), blank=True, null=True)


    class Meta:
        verbose_name = 'Сегмент'
        verbose_name_plural = 'Сегменты'


class FlightCancel(models.Model):
    transaction = models.ForeignKey(to=payment_model.Transaction, on_delete=models.CASCADE, verbose_name=_("Транзакция"), related_name="flight_cancel")
    flight = models.ForeignKey(to=FlightRequest, on_delete=models.CASCADE, verbose_name=_("Билет"))


    class Meta:
        verbose_name = _("Отмена брони")
        verbose_name_plural = verbose_name
        