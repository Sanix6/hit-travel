from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.hashers import make_password
import requests
from ..base.services import get_path_upload_photo, validate_size_image
from .services import add_tourist_on_user_creation, add_lead_on_creation
from .managers import UserManager
from src.main.models import Currency

class User(AbstractUser):
    GENDER_CHOICES = (
        ("м", "Муж"),
        ("ж", "Жен"),
        ("н", "Неизвестно"),
    )

    groups = models.ForeignKey(
        Group,
        verbose_name=_("groups"),
        null=True,
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
        on_delete=models.SET_NULL
    )
    username = None
    # balance = models.DecimalField(_("Balance"), default=0, max_digits=10, decimal_places=2)
    # bonuses = models.DecimalField(_("Bonuses"), default=0, max_digits=10, decimal_places=2)
    email = models.EmailField(_("Email"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    surname = models.CharField(_("Отчество"), null=True, blank=True, max_length=255)
    is_verified = models.BooleanField(_("Verification"), default=False)
    phone = models.CharField(_("Телефон"), max_length=100)
    whatsapp = models.CharField(_("What's App номер"), help_text='без (+, 0)      Для менеджеров', max_length=230, blank=True, null=True)
    password_readable = models.CharField(null=True, blank=True, max_length=255)
    verification_code = models.IntegerField(_("Verification code"), null=True, blank=True)
    verification_code_time = models.DateTimeField(_("Verification code created time"), null=True, blank=True)
    password_reset_token = models.CharField(_("Password Reset"), max_length=100, blank=True, null=True, unique=True)
    photo = models.ImageField(
        _("Аватар"), 
        upload_to=get_path_upload_photo,
        default="default.png",
        validators=[validate_size_image],
    )
    dateofborn = models.DateField(_("Дата рождения"), null=True, blank=True)
    gender = models.CharField(_("Пол"), choices=GENDER_CHOICES, max_length=3)
    
    inn = models.CharField(_("ИНН"), max_length=100, null=True, blank=True)
    date_of_issue = models.DateField(_("Дата выдачи"), null=True, blank=True)
    issued_by = models.CharField(_("Орган выдачи"), null=True, blank=True, max_length=100)
    validity = models.DateField(_("Срок действия"), null=True, blank=True)
    city = models.CharField(_("Город"), max_length=255, null=True, blank=True)
    passport_front = models.ImageField(_("Фото паспорта, передняя сторона"), upload_to="passports", null=True, blank=True)
    passport_back = models.ImageField(_("Фото паспорта, задняя сторона"), upload_to="passports",null=True, blank=True)
    passport_id = models.CharField(_("ID паспорт"), max_length=36, null=True, blank=True, unique=True)
    county = models.CharField(_("Страна"), max_length=100, null=True, blank=True)
    tourist_id = models.IntegerField(_("ID Туриста"), null=True, blank=True)
    bcard_number = models.CharField(_("Номер бонусного счёта"), max_length=255, null=True, blank=True)
    bcard_id = models.IntegerField(_("ID бонусного счёта"), null=True, blank=True)
    created = models.IntegerField(null=True, blank=True, default=1)
    first_name_en = models.CharField(_("Имя на латинице"), max_length=150, null=True, blank=True)
    last_name_en = models.CharField(_("Фамилия на латинице"), max_length=150, null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        db_table = "user"
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        
    def __str__(self):
        return self.email
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)
        self.password_readable = raw_password
        self._password = raw_password
    

@receiver(post_save, sender=User)
def add_tourist(sender, instance, created, **kwargs):
    if created:
        add_tourist_on_user_creation(sender, instance)


class BonusHistory(models.Model):
    CURRENCY_CHOICES = (
        ("СОМ", "СОМ"),
        ("USD", "USD")
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bonus_history")
    name = models.CharField(_("Название бонуса"), max_length=255)
    created_at = models.DateTimeField(_("Дата"))
    valid = models.DateField(_("Действителен до"))
    sum = models.IntegerField(_("Сумма"), default=0)
    currency = models.CharField(_("Валюта"), choices=CURRENCY_CHOICES, max_length=5, default="СОМ")
    
    def __str__(self):
        return self.user.email
    
    class Meta:
        verbose_name  = _("История бонусов")
        verbose_name_plural = _("История бонусов")
        

class RequestTour(models.Model):
    GENDER_CHOICES = (
        ("м", "Муж"),
        ("ж", "Жен")
    )
    STATUS_CHOICES = (
        (1, "Новая заявка"),
        (2, "В процессе покупки"),
        (3, "Тур куплен"),
        (4, "Отклонено"),
    )
    user = models.ForeignKey(User, verbose_name=_("Клиент"), on_delete=models.CASCADE, null=True, blank=True)
    status = models.IntegerField(_("Статус"), choices=STATUS_CHOICES, default=2)
    request_number = models.IntegerField(_("Номер заявки"), null=True, blank=True)
    manager = models.ForeignKey(User, verbose_name='Менеджер', on_delete=models.CASCADE, limit_choices_to={"groups__name": 'Managers'}, null=True, blank=True, related_name='tour_manager')
    
    first_name = models.CharField(_("Имя"), max_length=100, null=True, blank=True)
    last_name = models.CharField(_("Фамилия"), max_length=100, null=True, blank=True)
    phone = models.CharField(_("Телефон"), max_length=100, null=True, blank=True)
    email = models.EmailField(_("E-mail"), max_length=100, null=True, blank=True)
    gender = models.CharField(_("Пол"), choices=GENDER_CHOICES, max_length=3, null=True, blank=True)
    dateofborn = models.DateField(_("Дата рождения"), null=True, blank=True)
    
    # Passport Info
    inn = models.CharField(_("ИНН"), max_length=100, null=True, blank=True)
    passport_id = models.CharField(_("ID пасспорта"), max_length=255, null=True, blank=True)
    date_of_issue = models.DateField(_("Дата выдачи"), null=True, blank=True)
    issued_by = models.CharField(_("Орган выдачи"), null=True, blank=True, max_length=100)
    validity = models.DateField(_("Срок действия"), null=True, blank=True)
    city = models.CharField(_("Город"), max_length=255, null=True, blank=True)
    country = models.CharField(_("Страна"), max_length=255, null=True, blank=True)
    passport_front = models.ImageField(_("Фото паспорта, передняя сторона"), upload_to="passports", null=True, blank=True)
    passport_back = models.ImageField(_("Фото паспорта, задняя сторона"), upload_to="passports", null=True, blank=True)
    
    operatorlink = models.URLField(_("Ссылка на оператора"), max_length=1000, null=True, blank=True)
    price = models.CharField(_("Цена"), max_length=255, null=True, blank=True)
    paid = models.FloatField(_("Всего оплачено"), blank=True, null=True, help_text="в Сомах")
    currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.CASCADE)
    tourid = models.CharField(_("Код тура"), max_length=100, null=True, blank=True)
    bonuses = models.DecimalField(_("Бонусы"), default=0, max_digits=10, decimal_places=2, null=True, blank=True)
    pdf = models.FileField(_("Прикрепить PDF"), upload_to="agreements", null=True, blank=True)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True, null=True, blank=True)
    surcharge = models.CharField(_("Доплата"), max_length=255, default=10, null=True, blank=True)
    agreement = models.FileField(_("Договор"), upload_to="agreements", null=True, blank=True)
    payler_url = models.CharField(max_length=700, null=True, editable=False)
    transaction_id = models.CharField(max_length=700, null=True, editable=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        super(RequestTour, self).save(*args, **kwargs)
    
    def deadline(self):
        deadline = self.created_at + timedelta(days=10)
        return deadline.strftime('%d.%m.%Y %H:%M')
        
    class Meta:
        verbose_name = _("Заявка")
        verbose_name_plural = _("Заявки")


@receiver(post_save, sender=RequestTour)
def add_request(sender, instance, created, **kwargs):
    if created:
        # add_lead_on_creation(sender, instance)
        pass


class Document(models.Model):
    request = models.ForeignKey(RequestTour, on_delete=models.CASCADE, related_name="documents")
    name = models.CharField(_("Название документа"), max_length=255, null=True, blank=True)
    file = models.FileField(_("Документ"), upload_to="documents")
    created_at = models.DateField(_("Дата создания"), auto_now_add=True)
    
    def __str__(self) -> str:
        return str(self.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    
    class Meta:
        verbose_name = _("Документ")
        verbose_name_plural = _("Прикрепленные документы")


    
class Payments(models.Model):
    img = models.ImageField(_("QRCode"), upload_to="payments")
    description = RichTextField(_("Инструкция"), max_length=255)
    bank_name = models.CharField(_("Название банка"), null=True, blank=True, max_length=400)
    icon = models.ImageField(_("Иконка"), upload_to="payments", null=True, blank=True)
    
    class Meta:
        verbose_name = "Оплата"
        verbose_name_plural = "Платежи"
        
    def __str__(self):
        return self.bank_name
    

class FAQ(models.Model):
    question = models.CharField(_("Вопрос"), max_length=255)
    answer = RichTextField(_("Ответ"))
    
    def __str__(self) -> str:
        return self.question
    
    class Meta:
        verbose_name = _("FAQ")
        verbose_name_plural = _("FAQ")


class ManualRequests(models.Model):
    user = models.ForeignKey(User, verbose_name=_("Клиент"), on_delete=models.SET_NULL, null=True, blank=True)
    request_id = models.IntegerField(null=True)
    data = models.JSONField(default=dict, editable=False)

    class Meta:
        verbose_name = "Ручные заявки"
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.first_name


class RequestHotel(models.Model):
    STATUS_CHOICES = (
        (1, "Новая заявка"),
        (2, "В процессе"),
        (3, "Оплачено"),
        (4, "Отклонено"),
    )
    pdf = models.FileField(_("Прикрепить PDF"), upload_to="agreements", null=True, blank=True)
    status = models.IntegerField(_("Статус"), choices=STATUS_CHOICES, default=1)
    user = models.ForeignKey(User, verbose_name=_("Клиент"), on_delete=models.CASCADE, null=True, blank=True)
    hotelid = models.CharField(_("Код отеля"), max_length=100, null=True, blank=True)
    first_name = models.CharField(_("Имя"), max_length=100, null=True, blank=True)
    phone = models.CharField(_("Телефон"), max_length=100, null=True, blank=True)
    email = models.EmailField(_("E-mail"), max_length=100, null=True, blank=True)
    price = models.FloatField(_("К оплате"), blank=True, null=True)
    price_netto = models.FloatField(_('Цена (оригинальная)'), blank=True, null=True)
    meal = models.CharField(_('Питание'), null=True, blank=True)
    paid = models.FloatField(_("Всего оплачено"), blank=True, null=True, help_text="в Сомах", default=0)
    currency = models.ForeignKey(Currency, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True, null=True, blank=True)
    payler_url = models.CharField(max_length=700, null=True, editable=False)
    transaction_id = models.CharField(max_length=700, null=True, editable=False)
    nights = models.PositiveIntegerField(_('Количество ночей'), blank=True, null=True)
    flydate = models.DateField(_('Дата вылета'), blank=True, null=True)
    placement = models.CharField(_('Размещение'), max_length=10, blank=True, null=True)
    adults = models.PositiveIntegerField(_('Количество взрослых'), default=1)
    child = models.PositiveIntegerField(_('Количество детей'), default=0)
    mealcode = models.PositiveIntegerField(_('Код питания'), blank=True, null=True)
    mealrussian = models.CharField(_('Питание (на русском)'), max_length=255, blank=True, null=True)

    
    class Meta: 
        verbose_name = _("Заявка на отель")
        verbose_name_plural = _("Заявки на отели")


  
class Traveler(models.Model):
    GENDER_CHOICES = (
        ("Муж", "Муж"),
        ("Жен", "Жен")
    )
    
    main = models.ForeignKey(RequestTour, on_delete=models.CASCADE, related_name="travelers", null=True, blank=True)
    dateofborn = models.DateField(_("Дата рождения"), null=True, blank=True)
    first_name = models.CharField(_("Имя по загранпаспорту"), max_length=100)
    last_name = models.CharField(_("Фамилия по загранпаспорту"), max_length=100)
    # gender = models.CharField(_("Пол"), choices=GENDER_CHOICES, max_length=3, null=True, blank=True)
    # inn = models.CharField(_("Серия и номер"), max_length=100, null=True, blank=True)
    passport_id = models.CharField(_("Серия и номер з/п"), max_length=255, null=True, blank=True)
    # date_of_issue = models.DateField(_("Дата выдачи"), null=True, blank=True)
    issued_by = models.CharField(_("Орган, выдачи з/п"), null=True, blank=True, max_length=100)
    # validity = models.DateField(_("Срок действия"), null=True, blank=True)
    # city = models.CharField(_("Город"), max_length=255, null=True, blank=True)
    # country = models.CharField(_("Страна"), max_length=255, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Путешественник")
        verbose_name_plural = _("Путешественники")


class HotelTraveler(models.Model):
    GENDER_CHOICES = (
        ("Муж", "Муж"),
        ("Жен", "Жен")
    )
    hotel = models.ForeignKey(RequestHotel, on_delete=models.CASCADE, related_name="travelers", null=True, blank=True)
    dateofborn = models.DateField(_("Дата рождения"), null=True, blank=True)
    first_name = models.CharField(_("Имя по загранпаспорту"), max_length=100)
    last_name = models.CharField(_("Фамилия по загранпаспорту"), max_length=100)
    passport_id = models.CharField(_("Серия и номер з/п"), max_length=255, null=True, blank=True)
    issued_by = models.CharField(_("Орган, выдачи з/п"), null=True, blank=True, max_length=100)

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = _("Путешественник")
        verbose_name_plural = _("Путешественники")
