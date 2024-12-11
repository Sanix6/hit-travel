from django.conf import settings
from datetime import datetime
import requests
from config.celery import app
from .models import *
from django.db import transaction
from django.shortcuts import get_object_or_404
import logging
import  json
import redis
from .models import FlightRequest, Passengers, User  


AVIALOGIN = settings.AVIALOGIN
AVIAPASS = settings.AVIAPASS
AVIA_URL = settings.AVIA_URL



KEY = settings.KEY
AUTHLOGIN = settings.AUTHLOGIN
AUTHPASS = settings.AUTHPASS


logging.basicConfig(
    filename="myagent.log",  
    level=logging.INFO,          
    format="%(asctime)s - %(levelname)s - %(message)s", 
)

logging.basicConfig(level=logging.INFO)


def get_u_tk_id(passenger):
    if passenger.age == "adt":
        return 1 
    elif passenger.age == "chd":
        return 4  
    elif passenger.age in ("inf", "ins"):
        return 5  
    elif passenger.age == "src":
        return 1  
    elif passenger.age == "yth":
        return 1
    return 1

def create_avia(service_id, data):
    url = f"https://api.u-on.ru/{KEY}/avia/create.json"
    
    date_from = datetime.strptime(data.segments.first().date_from, "%d.%m.%Y")
    date_to = datetime.strptime(data.segments.first().date_to, "%d.%m.%Y")

    book_class_map = {
        "e": "Эконом",
        "b": "Бизнес класс",
        "f": "Первый класс",
        'w': "Комфорт"
    }
    book_class = book_class_map.get(data.book_class.lower(), "Неизвестный класс") 


    r_data = {
        "service_id": service_id,
        "at_dat_begin": date_from.strftime("%Y-%m-%d"),
        "at_time_begin": data.segments.first().time_from,
        "at_dat_end": date_to.strftime("%Y-%m-%d"),
        "at_time_end": data.segments.first().time_to, 
        "at_flight_number": f"{data.code}{data.flight_number}",
        "at_course_begin": data.segments.first().from_name,
        "at_course_end": data.segments.first().to_name,
        "at_class": book_class,
        "at_type": data.type, 
        "at_duration": f"{data.segments.first().duration_hour}ч, {data.segments.first().duration_minute}",
        "at_baggage": data.is_baggage,
        "provider": data.provider,
        "at_code_begin": data.segments.first().from_iata,
        "at_code_end": data.segments.first().to_iata,
        "at_time_begin": data.segments.first().time_from, 
        "at_time_end": data.segments.first().time_to,
    }

    logging.info(f"Request data for create_avia: {r_data}")  

    try:
        response = requests.post(url, data=r_data)
        logging.info(f"Response status: {response.status_code}, Response body: {response.text}") 
        if response.status_code == 200:
            logging.info("Создание авиатранспорта прошло успешно.")
            return True
        else:
            logging.error(f"Ошибка при создании авиатранспорта: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"Ошибка запроса в create_avia: {e}")
        return False


def create_service(request_number, data):
    url = f"https://api.u-on.ru/{KEY}/service/create.json"
    first_segment = data.segments.first()
    if not first_segment:
        raise ValueError("Нет доступных сегментов для создания сервиса.")

    chd_count = getattr(data, 'chd', 0)
    inf_count = getattr(data, 'inf', 0)
    adt_count = getattr(data, 'adt', 0)

    r_data = {
        "r_id": request_number,
        "type_id": 6,
        "description": f"Авиаперелет, Город вылета {first_segment.from_name}: Город прибытия {first_segment.to_name}, время в пути в минутах {first_segment.duration_minute}, время в пути в часах {first_segment.duration_hour}",
        "country": first_segment.from_country,
        "city": first_segment.from_name,
        "price": data.amount,
        "route": f"{first_segment.from_name} -> {first_segment.to_name}",
        "tourists_count": adt_count, 
        "tourists_child_count": chd_count,  
        "tourists_baby_count": inf_count,  
        "dat_begin": first_segment.date_from,
        "dat_end": first_segment.date_to,
    }
    response = requests.post(url, json=r_data)

    if response.status_code == 200:
        service_id = response.json().get("id")
        create_avia(service_id, data)
    else:
        raise ValueError(f"Ошибка при создании сервиса: {response.text}")


def add_tourist_avia(passengers):
    url = f"https://api.u-on.ru/{KEY}/user/create.json"
    passenger_ids = []

    for passenger in passengers:
        tourist_data = {
            "u_name": passenger.first_name, 
            "u_surname": passenger.last_name,
            "u_phone": passenger.phone,
            "u_email": passenger.email,
        }

        response = requests.post(url, json=tourist_data)
        if response.status_code == 200:
            response_json = response.json()
            passenger_ids.append(response_json.get("id"))
        else:
            print(f"Error: {response.status_code}, {response.text}")
            continue
    return passenger_ids


def create_request(data, user):
    url = f"https://api.u-on.ru/{KEY}/request/create.json"

    passengers = data.passengers.all()

    passenger_ids = add_tourist_avia(passengers)

    r_data = {
        "r_reservation_number": data.billing_number,
        "r_dat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "r_co_id": 3,
        "r_tour_operator_id": 117,
        "r_travel_type_id": 1,
        "u_type": 3,
        "u_surname": user.last_name,
        "u_name": user.first_name,
        "u_phone": data.client_phone,
        "u_phone_mobile": data.client_phone,
        "u_email": data.client_email,
        "source": "Мобильное приложение",
        "tourists": [
            {
                "u_name": passenger.first_name,
                "u_surname": passenger.last_name,
                "u_birthday": passenger.birthdate.strftime("%Y-%m-%d") if passenger.birthdate else None,
                "u_zagran_number": passenger.docnum,
                "u_zagran_expire": passenger.docexp.strftime("%Y-%m-%d") if passenger.docexp else None,
                "u_tk_id": get_u_tk_id(passenger),  
            }
            for passenger in passengers
        ]
    }

    response = requests.post(url, json=r_data)
    if response.status_code == 200:
        create_service(response.json()["id"], data=data)
    else:
        print(f"Error creating request: {response.status_code}, {response.text}")

        
@app.task()
def booking(token, book_url, id):
    flight = FlightRequest.objects.get(id=id)
    partner_affiliate_fee = flight.partner_affiliate_fee or 0 

    url = f"{AVIA_URL}/avia/book?auth_key={str(token)}&{str(book_url)}&partner_affiliate_fee={partner_affiliate_fee}"

    response = requests.get(url)

    with open("example.txt", "a") as file:
        file.write(f"{response.json()}\n\n")

    if response.json().get("success") == True:
        billing_number = str(response.json()["data"]["book"]["order"]["billing_number"])
        
        flight.billing_number = billing_number
        flight.save()

        return True
    else:
        return response.json()["data"].get("message", "Unknown error")

@app.task()
def ticketed(token, id):
    url = f"{AVIA_URL}/payment/pay-with-balance?auth_key={str(token)}&billing={id.billing_number}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return True
