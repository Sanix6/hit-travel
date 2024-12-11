import requests
from django.conf import settings
from datetime import datetime, timedelta
from .services import add_tourist
import logging
from .models import *
import redis
import json

logging.basicConfig(filename='service.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


KEY = settings.KEY
AUTHLOGIN = settings.AUTHLOGIN
AUTHPASS = settings.AUTHPASS
TOURVISOR_URL = "http://tourvisor.ru/xml/hotel.php"
UON_URL = f"https://api.u-on.ru/{KEY}/service/create.json"
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)



def create_hotel_service(request_number, data=None):
    hotel_id = data.get("id") 
    request_hotel = RequestHotel.objects.get(id=hotel_id) 
    
    tour_response = requests.get(
        f"http://tourvisor.ru/xml/hotel.php?authlogin={AUTHLOGIN}&authpass={AUTHPASS}&format=json&hotelcode={request_hotel.hotelid}"
    )
    tour_data = tour_response.json()["data"]["hotel"]

    uon_data = {
        "r_id": request_number,
        "type_id": 12,
        "description": f"Отель: {tour_data['name']}\nГород: {tour_data['region']}",
        "country": tour_data["country"],
        "city": tour_data["region"],
        "hotel": tour_data["name"],
        "price": request_hotel.price_netto,  
        "currency_id": 3,
        "tourists_count": request_hotel.adults,
    }

    response = requests.post(f"https://api.u-on.ru/{KEY}/service/create.json", data=uon_data)
    response.status_code == 200

def add_tourist(travelers):
    url = f"https://api.u-on.ru/{KEY}/user/create.json"  
    tourist_ids = []

    for user in travelers:
        tourist_data = {
            "u_name": user.get("first_name"),
            "u_surname": user.get("last_name"),
            "u_phone": user.get("phone"),  
            "u_email": user.get("email"),
        }

        response = requests.post(url, json=tourist_data)
        if response.status_code == 200:
            response_json = response.json()
            tourist_ids.append(response_json.get("id"))
        else:
            return None  

    return tourist_ids
       

def hotel_lead(data, user):
    url = f"https://api.u-on.ru/{KEY}/request/create.json"
    note = f"Заявки на отель №{data['hotelid']}"

    r_data = {
        # "r_id_internal": data.get("id"),
        "description": note,
        "r_dat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "r_dat_begin": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "r_co_id": 3,
        "r_tour_operator_id": 117,
        "r_travel_type_id": 7,
        "r_cl_id": user.tourist_id,
        "u_name": data.get("first_name"),
        "u_phone": data.get("phone"),
        "u_email": data.get("email"),
        "note": note,
        "source": "Мобильное приложение",
        "tourists": []
    }

    travelers = data.get("travelers", [])
    for traveler in travelers:
        r_data["tourists"].append({
            "u_name": traveler.get("first_name"),
            "u_surname": traveler.get("last_name"),
            "u_birthday": traveler.get("dateofborn"),
            "u_passport_number": traveler.get("passport_id"),
            "u_passport_taken": traveler.get("issued_by")
        })

    response = requests.post(url, json=r_data)

    if response.status_code == 200:
        response_data = response.json()
        create_hotel_service(response_data["id"], data=data)
        add_tourist(travelers)
        return True
    else:
        return False