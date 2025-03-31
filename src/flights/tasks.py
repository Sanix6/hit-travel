from datetime import timedelta

import redis
import requests
from celery import shared_task
from django.conf import settings
from django.utils import timezone
from urllib.parse import urlencode
import aiohttp
import asyncio

from src.payment.models import Transaction
from src.flights.models import FlightRequest

@shared_task(name="src.flights.tasks.timeout")
def timeout():
    from src.payment.models import Transaction  

    timeout_threshold = timezone.now() - timedelta(minutes=25)

    flight_requests = FlightRequest.objects.filter(
        status="booked", created_at__lte=timeout_threshold
    )

    request_ids = flight_requests.values_list("request_id", flat=True)

    Transaction.objects.filter(request_id__in=request_ids).update(status="timeout")

    flight_requests.update(status="timeout")



@shared_task()
def get_auth_key():
    try:
        avia_center_url = settings.AVIA_URL
        url = f"{avia_center_url}/user/login"

        data = {"login": settings.AVIALOGIN, "password": settings.AVIAPASS}

        response = requests.post(url, data=data)

        if response.status_code == 200:
            token = response.json().get("data", {}).get("auth_token", "")
            if token:
                redis_client = redis.StrictRedis(host="localhost", port=6379, db=2)
                redis_client.set("cancel_token", token)
                redis_client.expire("cancel_token", 3600)
            raise Exception(
                f"Ошибка при получении токена: {response.status_code}, {response.text}"
            )
    except Exception as e:
        print(f"Ошибка в задаче получения токена: {str(e)}")

