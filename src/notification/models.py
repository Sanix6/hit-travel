from django.db import models
import uuid
from django.utils.translation import gettext_lazy as _
from .tasks import send_notification


class CustomNotification(models.Model):
    text = models.TextField(_("Текст"), max_length=400)
    all_users = models.BooleanField(default=False, verbose_name="Выбрать всех пользователей")
    selected_users = models.ManyToManyField(to="UserToken", blank=True, verbose_name="Выбрать пользователей")
    sent = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = _("Создать уведомление")
        verbose_name_plural = _("Создать уведомление")

    def save(self, *args, **kwargs):
        if not self.sent:
            if self.all_users:
                users = UserToken.objects.all()
            else:
                users = self.selected_users.all()
            text = self.text
            send_notification.delay(text, *users)
            print("Notification sent")
            self.sent = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.text
    

class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        max_length=36
    )

    class Meta:
        abstract = True


class TokenFCM(BaseModel):
    token = models.CharField(
        max_length=256,
        verbose_name=_('Токен'),
        unique=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    class Meta:
        verbose_name = _('Токен')
        verbose_name_plural = _('Токены (Уведомление)')


class UserToken(BaseModel):
    user = models.ForeignKey(
        to='account.User',
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='tokens'
    )
    token = models.ForeignKey(
        to=TokenFCM,
        on_delete=models.CASCADE,
        related_name='users'
    )
    is_active = models.BooleanField(
        default=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        blank=True, null=True,
        verbose_name=_('Дата изменения')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Дата создания')
    )

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Токен пользователя')
        verbose_name_plural = _('Токены пользователей (Уведомление)')

    