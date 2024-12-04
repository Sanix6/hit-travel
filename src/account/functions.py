import requests
from django.conf import settings
from datetime import datetime, timedelta
from .services import add_tourist
import logging
import redis
import json

logging.basicConfig(filename='service.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


KEY = settings.KEY
AUTHLOGIN = settings.AUTHLOGIN
AUTHPASS = settings.AUTHPASS
TOURVISOR_URL = "http://tourvisor.ru/xml/hotel.php"
UON_URL = f"https://api.u-on.ru/{KEY}/service/create.json"
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)


def create_hotel_service(hotelcode, data=None):
    redis_key = f"hotel:{hotelcode}"
    
    hotel_data = redis_client.get(redis_key)
    if not hotel_data:
        logging.error(f"Ключ {redis_key} отсутствует в Redis.")
        return False

    try:
        hotel_data = json.loads(hotel_data)
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка декодирования JSON для ключа {redis_key}: {e}")
        return False

    logging.info(f"Данные из Redis успешно извлечены для hotelcode={hotelcode}")
    
    hotel_name = hotel_data.get('hotelname', 'Unknown')
    hotel_stars = hotel_data.get('hotelstars', 'N/A')
    country = hotel_data.get('countryname', 'Unknown')
    region = hotel_data.get('regionname', 'Unknown')

    tours_info = "" 
    
    post_data = {
        # "r_id": data.get('id', None),
        "type_id": 12,
        "description": (
            f"Название отеля: {hotel_name}\n"
            f"Рейтинг: {hotel_stars} звезд\n"
            f"Страна: {country}\n"
            f"Регион: {region}\n"
            f"{tours_info}" 
        ),
        "date_begin": None, 
        "country": country,
        "city": region,
        "hotel": hotel_name,
        "hotel_type": hotel_stars,
        "nutrition": None,  
        "price": None,  
        "currency": "EUR",
        "currency_id": 2,
        "currency_id_netto": 2,
    }
    print(post_data)

    url = f"https://api.u-on.ru/{KEY}/service/create.json"
    try:
        response = requests.post(url, json=post_data)
        if response.status_code == 200:
            logging.info(f"Запрос к U-ON API успешен для hotelcode={hotelcode}, ответ: {response.json()}")
        else:
            logging.error(f"Ошибка запроса к U-ON API для hotelcode={hotelcode}: {response.status_code}, текст ошибки: {response.text}")
    except requests.RequestException as e:
        logging.error(f"Ошибка соединения с U-ON API для hotelcode={hotelcode}: {e}")

    return True


    
def hotel_lead(data, user, instance=None):
    url = f"https://api.u-on.ru/{KEY}/request/create.json"
    
    hotel_code = data.get("hotelcode") 
    if not hotel_code:
        logging.error("Отсутствует hotelcode")
        print(hotel_code)
        return False
    
    note = f"Заявки на отель\n"
    
    travelers = data.get("travelers", [])
    tourist_ids = add_tourist(travelers) 
    r_data = {
        "r_id_internal": data.get("id"),
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
        "tourists": [
            {
                "u_name": traveler.get("first_name"),
                "u_surname": traveler.get("last_name"),
                "u_birthday": traveler.get("dateofborn"),
                "u_passport_number": traveler.get("passport_id"),
                "u_passport_taken": traveler.get("issued_by")
            } for traveler in travelers
        ]
    }
    print(r_data)

    response = requests.post(url)

    if response.status_code == 200:
        response_data = response.json()
        data['id'] = response_data.get('id')

        create_hotel_service(hotel_code, data=data) 

        return response_data
    else:
        logging.error(f"Ошибка запроса к U-ON API: {response.status_code}, текст ошибки: {response.text}")
        return False