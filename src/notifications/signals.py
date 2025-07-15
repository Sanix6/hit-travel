import os
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from bs4 import BeautifulSoup
from .models import Notifications
from .service import NotificationApi

API = NotificationApi()

def send_notification(instance, player_ids=None):
    if not instance.title or not instance.description:
        return "Данные не представлены"

    data = {
        "contents": {"en": BeautifulSoup(instance.description, 'html.parser').text},
        "headings": {"en": instance.title},
        "big_picture": instance.image.url if instance.image else None
    }

    if player_ids:
        data["include_player_ids"] = player_ids
    else:
        data["included_segments"] = ["All"]

    API.create_notification(**data)


@receiver(post_save, sender=Notifications)
def create_notification(sender, instance, created, **kwargs):
    if created and instance.sendtoall:
        send_notification(instance)


@receiver(m2m_changed, sender=Notifications.devices.through)
def notification_users_changed(sender, instance, action, **kwargs):
    if action == "post_add" and not instance.sendtoall:
        player_ids = list(instance.devices.values_list("device_token", flat=True))
        if player_ids:
            send_notification(instance, player_ids)

