from celery import shared_task
from django.conf import settings
from onesignal_sdk.client import Client

from src.flights.models import FlightRequest

app_id = settings.ONESIGNAL_APPID
rest_api = settings.ONESIGNAL_RESTAPI


@shared_task
def send_notification(text, user_tokens):
    onesignal_client = Client(app_id=app_id, rest_api_key=rest_api)

    notification_data = {"contents": {"en": text}, "include_player_ids": user_tokens}

    try:
        onesignal_response = onesignal_client.send_notification(notification_data)

        if onesignal_response.status_code == 200:
            print(f"Notification sent successfully: {onesignal_response}")
        else:
            print(
                f"Failed to send notification: {onesignal_response.status_code} - {onesignal_response}"
            )
    except Exception as e:
        print(f"Error while sending notification: {str(e)}")


@shared_task()
def begin_notification():
    from datetime import date, timedelta

    target_date = date.today() + timedelta(days=1)

    data = FlightRequest.objects.filter(begin_date=target_date)

    users_with_tokens = []
    for request in data:
        user = request.user
        tokens = getattr(user, "tokens", None)
        if tokens is not None:
            users_with_tokens.append(user)

    avia_text = "Напоминаем, что завтра вас ждет умопомрачительный полет!"

    send_notification.delay(avia_text, *users_with_tokens)
