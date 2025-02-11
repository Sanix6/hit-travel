from datetime import datetime

import requests
from django.conf import settings

from .models import BusTours

KEY = settings.KEY


def create_service(data, user, request_number):
    url = f"https://api.u-on.ru/{KEY}/service/create.json"

    service_data = {
        "r_id": request_number,
        "type_id": 17,
        "description": f"Автобусный тур: {data['title']}\nСсылка: ",
        "nights": data.get("nights"),
        "country": data.get("country"),
        "city": data.get("city"),
        "nutrition": data.get("meal"),
        "duration": f"{data.get('nights', 0)} ночей",
        "tourists_count": len(data.get("bustour_travelers", [])) + 1,
        "price": data.get("price"),
        "currency": "KGZ",
        "currency_id": 6,
    }

    requests.post(url, data=service_data)


def send_bustour_request(data, user):
    url = f"https://api.u-on.ru/{KEY}/request/create.json"

    note = f"Страна: {data['country']}\n" f"Город: {data['city']}\n"

    r_data = {
        "r_dat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "r_cl_id": user.tourist_id,
        "r_dat_begin": data["datefrom"],
        "r_dat_end": data["dateto"],
        "u_surname": data["last_name"],
        "u_name": data["first_name"],
        "u_phone": data["phone"],
        "u_email": data["email"],
        "r_co_id": 3,
        "r_tour_operator_id": 117,
        "r_travel_type_id": 10,
        "note": note,
        "source": "Мобильное приложение",
        "nights_from": data["nights"],
        "nutrition": data["meal"],
        "tourist_count": data["num_of_tourists"],
        "budget": data["price"],
        "travel_type_id": 10,
    }

    res = requests.post(url, data=r_data)

    create_service(data, user, res.json()["id"])

    if res.status_code != 200:
        return False
    return res.json()
