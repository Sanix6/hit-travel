import os
import django
from celery import Celery
from celery.schedules import crontab
import redis
from django.conf import settings
import requests
from datetime import timedelta


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

app = Celery('config')

app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = 'Asia/Bishkek'

app.autodiscover_tasks(['src.search.avia_tasks', 'src.notification', 'src.webhooks'])

redis_client = redis.StrictRedis(host='localhost', port=6379, db=1)

app.conf.broker_connection_retry_on_startup = True


@app.task()
def get_token():
    from django.conf import settings
    avia_center_url = settings.AVIA_URL
    url = f"{avia_center_url}/user/login"
    data = {'login': settings.AVIALOGIN, 'password': settings.AVIAPASS}
    response = requests.post(url, data=data)
    redis_client.set('token', response.json()["data"]["auth_token"])
    print("Task Done)")


app.conf.beat_schedule = {
    "get-token-task": {
        "task": "config.celery.get_token",
        "schedule": timedelta(minutes=40),
    },
    "flights-timeout": {
        "task": "src.flights.tasks.timeout",
        "schedule": timedelta(minutes=1),
    },
    "notification": {
        "task": "src.notification.tasks.begin_notification",
        "schedule": crontab(hour=14, minute=0),
        # "schedule": timedelta(minutes=1),
    },
    "get-cancel-token-task": {
        "task": "src.flight.tasks.get_auth_key",
        "schedule": crontab(minute=0, hour="*"),
    }
}

