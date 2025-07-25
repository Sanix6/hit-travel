import logging
from datetime import datetime, timedelta

import pdfkit
import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.utils.translation import gettext_lazy as _
from num2words import num2words
from src.base.utils import Util
from src.account import models


KEY = settings.KEY
AUTHLOGIN = settings.AUTHLOGIN
AUTHPASS = settings.AUTHPASS
TOURVISOR_URL = "http://tourvisor.ru/xml/hotel.php"
UON_URL = f"https://api.u-on.ru/{KEY}/service/create.json"

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def hotel_request_exists(hotel_id, user):
    return models.RequestHotel.objects.filter(hotelid=hotel_id, user=user).exists()



def update_user(data, user):
    """Updates user data and syncs with the external U-ON API."""
    url = f"https://api.u-on.ru/{KEY}/user/update/{user.tourist_id}.json"

    u_sex = "m" if data.get("gender") == "м" else "f"

    r_data = {
        "u_birthday": data.get("dateofborn"),
        "u_zagran_given": data.get("date_of_issue"),
        "u_zagran_expire": data.get("validity"),
        "u_zagran_organization": data.get("issued_by"),
        "u_zagran_number": data.get("passport_id"),
        "u_sex": u_sex,
        "u_inn": data.get("inn"),
    }

    user.dateofborn = data.get("dateofborn")
    user.date_of_issue = data.get("date_of_issue")
    user.validity = data.get("validity")
    user.issued_by = data.get("issued_by")
    user.passport_id = data.get("passport_id")
    user.inn = data.get("inn")
    user.save()

    response = requests.post(url, json=r_data)
    response.raise_for_status()
    logging.info("User data updated successfully.")


def get_user_by_phone(phone):
    """Fetches a user by phone number from the U-ON API."""
    url = f"https://api.u-on.ru/{KEY}/user/phone/{phone}.json"
    response = requests.get(url)
    if response.status_code == 200:
        logging.info("User fetched successfully by phone.")
        return response.json().get("users", [])[0]
    return None


def bonus_card_create(user):
    """Creates and activates a bonus card for a user."""
    data_1 = {
        "number": f"{user.bcard_number}000",
        "user_id": int(user.tourist_id),
    }

    url_1 = f"https://api.u-on.ru/{KEY}/bcard/create.json"
    res_1 = requests.post(url_1, json=data_1)
    res_1.raise_for_status()

    bcard_id = res_1.json().get("id")
    user.bcard_id = bcard_id
    user.save()

    data_2 = {"bc_number": f"{user.bcard_number}000", "user_id": int(user.tourist_id)}
    url_2 = f"https://api.u-on.ru/{KEY}/bcard-activate/create.json"
    requests.post(url_2, json=data_2).raise_for_status()
    logging.info("Bonus card created and activated successfully.")
    return True


def create_dogovor(instance):
    """Generates a PDF agreement for the given instance."""
    date = datetime.now().strftime("%d.%m.%Y %H:%M")
    price_word = num2words(float(instance.price), lang="ru")
    surcharge_word = num2words(int(instance.surcharge), lang="ru")

    tour = requests.get(
        f"https://hit-travel.org/api/detail/tour/{instance.tourid}"
    ).json()

    context = {
        "obj": instance,
        "date": date,
        "price_word": price_word,
        "surcharge_word": surcharge_word,
        "operatorname": tour.get("tour", {}).get("operatorname", ""),
        "flydate": tour.get("tour", {}).get("flydate", ""),
        "nights": tour.get("tour", {}).get("nights", ""),
    }

    template = get_template("index.html")
    html = template.render(context)

    pdf = pdfkit.from_string(html, False)
    instance.agreement.save(
        f"agreement_pdf_{instance.request_number}.pdf",
        ContentFile(pdf),
        save=True,
    )
    logging.info("Agreement PDF generated successfully.")


def add_tourist(travelers):
    """Adds multiple travelers to the U-ON system."""
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
            tourist_ids.append(response.json().get("id"))
        else:
            logging.error(f"Failed to add tourist: {response.text}")
            return None

    logging.info("All tourists added successfully.")
    return tourist_ids


def create_avia_from_tour(tour_data, service_id):
    """Creates aviation details for the given tour data."""
    url = f"https://api.u-on.ru/{KEY}/avia/create.json"

    book_class_map = {
        "Y": "Эконом",
        "C": "Бизнес класс",
        "F": "Первый класс",
    }

    flights = tour_data.get("flights", [])
    if not flights:
        logging.error("No flight data available.")
        return False

    forward_flight = flights[0].get("forward", [])[0]
    backward_flight = flights[0].get("backward", [])[0]

    if not forward_flight or not backward_flight:
        logging.error("Incomplete flight data.")
        return False

    try:
        r_data = {
            "service_id": service_id,
            "at_dat_begin": forward_flight["departure"]["date"],
            "at_time_begin": forward_flight["departure"]["time"],
            "at_dat_end": backward_flight["departure"]["date"],
            "at_time_end": backward_flight["departure"]["time"],
            "at_flight_number": forward_flight["number"],
            "at_course_begin": forward_flight["departure"]["port"]["name"],
            "at_course_end": forward_flight["arrival"]["port"]["name"],
            "at_class": book_class_map.get(
                forward_flight["class"], "Неизвестный класс"
            ),
            "at_type": "RT",
            "at_duration": None,
            "at_baggage": forward_flight.get("baggage"),
            "provider": tour_data.get("operatorname", "Неизвестный оператор"),
            "at_code_begin": forward_flight["departure"]["port"]["id"],
            "at_code_end": forward_flight["arrival"]["port"]["id"],
        }

        response = requests.post(url, json=r_data)
        response.raise_for_status()
        logging.info("Aviation data created successfully.")
        return True
    except requests.RequestException as e:
        logging.error(f"Error creating aviation data: {e}")
        return False


def create_service(request_number, data=None, instance=None):
    url = f"https://api.u-on.ru/{KEY}/service/create.json"

    tourid = (
        data.get("tourid")
        if isinstance(data, dict)
        else getattr(data, "tourid", None) or getattr(instance, "tourid", None)
    )
    if not tourid:
        return False

    tour_url = f"http://tourvisor.ru/xml/actualize.php?authlogin={AUTHLOGIN}&authpass={AUTHPASS}&format=json&tourid={tourid}"
    tour_response = requests.get(tour_url)

    if tour_response.status_code != 200:
        return False

    tour_data = tour_response.json().get("data", {}).get("tour", {})
    if not tour_data:
        return False

    post_data = {
        "r_id": data["id"],
        "type_id": 12,
        "description": (
            f"Тур: {tour_data.get('tourname', 'Unknown')}\n"
            f"Город вылета: {tour_data.get('departurename', 'Unknown')}\n"
            f"Оператор: {tour_data.get('operatorname', 'Unknown')}"
        ),
        "date_begin": tour_data.get("flydate", ""),
        "country": tour_data.get("countryname", ""),
        "city": tour_data.get("hotelregionname", ""),
        "nutrition": tour_data.get("meal", ""),
        "duration": tour_data.get("nights", 0),
        "tourists_count": tour_data.get("adults", 0),
        "tourists_child_count": tour_data.get("child", 0),
        "tourists_baby_count": tour_data.get("infants", 0),
        "hotel": tour_data.get("hotelname", ""),
        "hotel_type": tour_data.get("room", ""),
        "price": tour_data.get("price"),
        "currency": tour_data.get("currency", ""),
        "currency_id": 3,
        "currency_id_netto": 3,
    }

    response = requests.post(url, data=post_data)
    if response.status_code == 200:
        service_id = response.json().get("id")
        create_avia_from_tour(tour_data, service_id)
        return response.json()
    return False


def create_lead(data, user, instance=None):
    url = f"https://api.u-on.ru/{KEY}/request/create.json"

    # update_user(data, user)

    tourid = (
        data.get("tourid")
        if isinstance(data, dict)
        else getattr(data, "tourid", None) or getattr(instance, "tourid", None)
    )
    if not tourid:
        return False

    tour_url = f"http://tourvisor.ru/xml/actualize.php?authlogin={AUTHLOGIN}&authpass={AUTHPASS}&format=json&tourid={tourid}"
    tour_response = requests.get(tour_url)

    if tour_response.status_code != 200:
        return False

    tour_data = tour_response.json().get("data", {}).get("tour", {})
    if not tour_data:
        return False

    flydate_str = tour_data.get("flydate", "")
    nights = int(tour_data.get("nights", 0))

    try:
        flydate = datetime.strptime(flydate_str, "%d.%m.%Y")
        datebackward = (flydate + timedelta(days=nights)).strftime("%d.%m.%Y")
    except ValueError:
        datebackward = ""

    r_data = {
        "r_dat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "r_dat_begin": flydate_str,
        "r_dat_end": datebackward,
        "currency": tour_data.get("currency", ""),
        "r_co_id": 3,
        "r_tour_operator_id": 117,
        "r_travel_type_id": 2,
        "reservation_number": data.get("request_number"),
        "u_surname": data.get("last_name"),
        "u_name": data.get("first_name"),
        "u_phone": data.get("phone"),
        "u_email": data.get("email"),
        "note": f"Оператор: {data.get('operatorlink', 'Unknown')},\n",
        "source": "Мобильное приложение",
        "tourists": [
            {
                "u_name": traveler.get("first_name"),
                "u_surname": traveler.get("last_name"),
                "u_birthday": traveler.get("dateofborn"),
                "u_zagran_number": traveler.get("passport_id"),
                "u_zagran_organization": traveler.get("issued_by"),
                "u_tk_id": tour_data.get("adults", 0),
            }
            for traveler in data.get("travelers", [])
        ],
    }

    res = requests.post(url, json=r_data)

    if res.status_code == 200:
        response_data = res.json()
        data["id"] = response_data.get("id")
        add_tourist(data.get("travelers", []))
        create_service(response_data.get("id"), data=data)
        return response_data
    return False


def decrease_bonuses(bcard_id, bonuses, reason):
    url = f"https://api.u-on.ru/{KEY}/bcard-bonus/create.json"

    data = {
        "bc_id": bcard_id,
        "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "type": 2,
        "bonuses": bonuses,
        "reason": reason,
    }

    res = requests.post(url, data=data)

    if res.status_code != 200:
        return False
    return True


def add_lead_on_creation(sender, instance):
    url = f"https://api.u-on.ru/{KEY}/request/create.json"

    if instance.user:
        user = instance.user
        instance.email = user.email
        instance.phone = user.phone
        instance.first_name = user.first_name
        instance.last_name = user.last_name
        instance.gender = user.gender
        instance.dateofborn = user.dateofborn
        instance.inn = user.inn
        instance.passport_id = user.passport_id
        instance.date_of_issue = user.date_of_issue
        instance.issued_by = user.issued_by
        instance.validity = user.validity
        instance.city = user.city
        instance.country = user.county
        instance.passport_front = user.passport_front
        instance.passport_back = user.passport_back
        instance.save()

    note = f"Оператор: {instance.operatorlink}\n"

    data = {
        "r_dat": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "r_cl_id": instance.user.tourist_id,
        "u_surname": instance.last_name,
        "u_name": instance.first_name,
        "u_phone": instance.phone,
        "u_email": instance.email,
        "note": note,
        "source": "Мобильное приложение",
    }

    res = requests.post(url, data)

    instance.request_number = res.json()["id"]
    instance.save()

    if instance.tourid:
        create_service(res.json()["id"], instance=instance)
        create_dogovor(instance)


def send_password_to_user(instance, password):
    email_body = (
        f"Привет! {instance.last_name} {instance.first_name}\n\n"
        f"Чтобы войти в нашу систему, используйте этот адрес электронной почты и пароль:\n\n"
        f"{instance.email}\n"
        f"{password}"
    )

    email_data = {
        "email_body": email_body,
        "email_subject": "Подтвердите регистрацию",
        "to_email": instance.email,
    }

    Util.send_email(email_data)


def add_tourist_on_user_creation(sender, instance):
    url = f"https://api.u-on.ru/{KEY}/user/create.json"

    if instance.groups:
        return

    data = {
        "u_surname": instance.last_name,
        "u_name": instance.first_name,
        "u_sname": instance.surname,
        "u_email": instance.email,
        "u_phone_mobile": instance.phone,
        "u_birthday": instance.dateofborn,
        "u_inn": instance.inn,
        "u_zagran_number": instance.inn,
        "u_zagran_given": instance.date_of_issue,
        "u_zagran_expire": instance.validity,
        "u_zagran_organization": instance.issued_by,
        "u_birthday_place": f"{instance.city} {instance.county}",
        "u_password": instance.password_readable,
        "u_sex": instance.gender,
    }

    res = requests.post(url, data)

    if res.status_code != 200:
        return False

    instance.tourist_id = res.json()["id"]
    instance.is_verified = True
    instance.save()
    # bonus_card_create(instance)

    return
