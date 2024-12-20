import requests

app_id = "b88ee836-3b76-4efa-9de4-10d2cc285e2c"
rest_api = "os_v2_app_xchoqnr3ozhpvhpecdjmykc6fr3f5evwgwveeauymedh4qc73us32ypyfmkfpr42qpv3cahst45whoef4fw4qdukq5rpdcjkzdfzmhi"

url = "https://onesignal.com/api/v1/notifications"
headers = {
    "Authorization": f"Basic {rest_api}",
    "Content-Type": "application/json",
}
payload = {
    "app_id": app_id,
    "contents": {"en": "Тестовое уведомление"},
    "include_external_user_ids": ["test_user_id"],  # Замените на реальные ID, если есть
}

response = requests.post(url, json=payload, headers=headers)

if response.status_code == 200:
    print("Уведомление отправлено успешно")
else:
    print(f"Ошибка: {response.status_code}, {response.text}")
