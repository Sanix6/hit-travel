from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor_uploader.fields import RichTextUploadingField
from src.account.models import User

class DeviceToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="device_tokens")
    device_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Пользователь: {self.user or 'Не указан'}, Устройство: {self.device_token}"

    class Meta:
        verbose_name = 'Токен устройства'
        verbose_name_plural = 'Токен устройства'


class Notifications(models.Model):
    devices = models.ManyToManyField("DeviceToken", blank=True)
    title = models.CharField(_('Уведомление'),  max_length=255)
    description = RichTextUploadingField(_("Описание"),config_name='default', blank=True, null=True)
    sendtoall = models.BooleanField(_("Отправить всем"), default=True)
    image = models.ImageField(_('Изображение'), upload_to='notifications/', null=True, blank=True)

    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'