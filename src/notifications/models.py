import uuid
import logging
from django.db import models
from django.utils.translation import gettext_lazy as _
from .tasks import send_notification
from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

class CustomNotification(models.Model):
    text = models.TextField(_("Текст"), max_length=400)
    all_users = models.BooleanField(
        default=False, verbose_name="Выбрать всех пользователей"
    )
    selected_users = models.ManyToManyField(
        to="UserToken", blank=True, verbose_name="Выбрать пользователей"
    )
    sent = models.BooleanField(default=False, editable=False)

    class Meta:
        verbose_name = _("Создать уведомление")
        verbose_name_plural = _("Создать уведомление")

    def __str__(self):
        return self.text


@receiver(post_save, sender=CustomNotification)
def send_push_notification(sender, instance, created, **kwargs):
    if created and not instance.sent:
        if instance.all_users:
            users = UserToken.objects.filter(is_active=True)
        else:
            users = instance.selected_users.filter(is_active=True)

        user_tokens = list(users.values_list("token__token", flat=True))

        if user_tokens:
            send_notification.delay(instance.text, user_tokens)
            logger.info("Notification sent to %d users", len(user_tokens))

        instance.__class__.objects.filter(id=instance.id).update(sent=True)


class BaseModel(models.Model):
    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )

    class Meta:
        abstract = True


class TokenFCM(BaseModel):
    token = models.CharField(max_length=256, verbose_name=_("Токен"), unique=True)
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата создания")
    )

    def __str__(self):
        return self.token

    class Meta:
        verbose_name = _("Токен")
        verbose_name_plural = _("Токены (Уведомление)")


class UserToken(BaseModel):
    user = models.ForeignKey(
        to="account.User",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="tokens",
    )
    token = models.ForeignKey(
        to=TokenFCM, on_delete=models.CASCADE, related_name="users"
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(
        auto_now=True, blank=True, null=True, verbose_name=_("Дата изменения")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Дата создания")
    )

    def __str__(self):
        return str(self.user)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Токен пользователя")
        verbose_name_plural = _("Токены пользователей (Уведомление)")
