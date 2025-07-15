import requests
from django.conf import settings

class NotificationApi:
    BASE_URL = "https://onesignal.com/api/v1/notifications"

    def __init__(self):
        self.app_id = settings.ONE_SIGNAL_APP_ID
        self.api_key = settings.ONE_SIGNAL_REST

        if not self.app_id or not self.api_key:
            raise ValueError("Переменные настройки ONE_SIGNAL_APP_ID и ONE_SIGNAL_REST не заданы в settings.py!")

        self.headers = {
            "Authorization": f"Basic {self.api_key}",
            "Content-Type": "application/json"
        }

    def create_notification(self, contents, headings, **kwargs):
        payload = {"app_id": self.app_id, "contents": contents, "headings": headings, **kwargs}

        try:
            response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"error": str(e)}
