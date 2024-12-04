# base
from django.db import models
from django.utils.translation import gettext_lazy as _
# additional
from django.contrib.auth import get_user_model
import uuid
import random

from .choices import *

User = get_user_model()

class Transaction(models.Model):        
    rid = models.CharField(
        _("Реквизит"),
        max_length=6,
        unique=True,
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qid = models.CharField(_("QID"), max_length=450, blank=True, null=True)
    status = models.CharField(_("Статус"), choices=TRANSACTION_STATUS, max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_transactions')
    name = models.CharField(_("Платёж для"), choices=TRANSACTION_TYPE, max_length=255)
    request_id = models.UUIDField(editable=True, blank=True, null=True, verbose_name=_("Айди авиа"))
    tour_id = models.IntegerField(_("Айди тура"), blank=True, null=True)
    hotel_id = models.IntegerField(_("Айди отеля"), blank=True, null=True)
    amount = models.FloatField(_("Сумма для платежа"))
    created_at = models.DateTimeField(_("Дата создания"), auto_now_add=True)

    @classmethod
    def generate_unique_code(cls):
        while True:
            code = str(random.randint(100000, 999999))
            if not cls.objects.filter(rid=code).exists():
                return code
            
    class Meta:
        verbose_name = _("Платеж")
        verbose_name_plural = _("Платежы")

    def __str__(self):
        return f"{self.user} - {self.amount} KGS"
    