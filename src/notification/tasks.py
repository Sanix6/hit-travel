from django.conf import settings
from onesignal_sdk.client import Client
from src.flights.models import FlightRequest
# from config.celery import app

from celery import shared_task

app_id = settings.ONESIGNAL_APPID
rest_api = settings.ONESIGNAL_RESTAPI

@shared_task()
def send_notification(text, *users):
    onesignal_client = Client(app_id=app_id, rest_api_key=rest_api)

    notification_data = {
        "contents": {"en": f"{text}"},
        "include_player_ids": [user.tokens.token.token for user in users]
    }
    try:
        onesignal_response = onesignal_client.send_notification(notification_data)
        response_data = {
            "status": onesignal_response.status_code,
            "body": onesignal_response.body
        }
        if onesignal_response.status_code == 200:
            print("OneSignals - res: True")
        else:
            print("OneSignals - res: False")
    except Exception as e:
        print(f"{str(e)}")


@shared_task()
def begin_notification():
    from datetime import date, timedelta

    target_date = date.today() + timedelta(days=1)

    data = FlightRequest.objects.filter(begin_date=target_date)

    users_with_tokens = []
    for request in data:
        user = request.user
        tokens = getattr(user, 'tokens', None)
        if tokens is not None:
            users_with_tokens.append(user)

    avia_text = "Напоминаем, что завтра вас ждет умопомрачительный полет!"
    
    send_notification.delay(avia_text, *users_with_tokens)