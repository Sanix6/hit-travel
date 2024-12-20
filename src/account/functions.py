import requests
from django.conf import settings
from datetime import datetime
from django.core.files.base import ContentFile
from django.template.loader import get_template
import pdfkit
from num2words import num2words
from .models import Currency, RequestTour, RequestHotel
from .services import decrease_bonuses
from src.payment.models import Transaction

KEY = settings.KEY
AUTHLOGIN = settings.AUTHLOGIN
AUTHPASS = settings.AUTHPASS
TOURVISOR_URL = "http://tourvisor.ru/xml/hotel.php"
UON_URL = f"https://api.u-on.ru/{KEY}/service/create.json"


def tour_request_exists(tour_id, user):
    """Проверка на существование заявки."""
    return RequestTour.objects.filter(tourid=tour_id, user=user).exists()


def update_tour_request_with_lead(tour_request, lead_response, data):
    """Обновление заявки с данными лида."""
    tour_request.request_number = lead_response["id"]
    tour_request.paid = float(data["bonuses"])
    tour_request.save()


def generate_and_save_pdf(tour_request, tour_id):
    """Генерация PDF и сохранение."""
    tour = requests.get(f"https://hit-travel.org/api/detail/tour/{tour_id}")
    if tour.status_code != 200:
        return False

    date = datetime.now().strftime("%d.%m.%Y %H:%M")
    price_word = num2words(float(tour_request.price), lang="ru")
    surcharge_word = num2words(int(tour_request.surcharge), lang="ru")
    context = {
        "obj": tour_request,
        "date": date,
        "price_word": price_word,
        "surcharge_word": surcharge_word,
        "operatorname": tour.json()["tour"]["operatorname"],
        "flydate": tour.json()["tour"]["flydate"],
        "nights": tour.json()["tour"]["nights"],
    }
    template = get_template("index.html")
    html = template.render(context)
    pdf = pdfkit.from_string(html, False)

    tour_request.agreement.save(
        f"agreement_pdf_{tour_request.id}.pdf",
        ContentFile(pdf),
        save=True,
    )
    return True


def create_transaction(tour_request, data, user):
    """Создание транзакции и генерация deeplink."""
    try:
        currency = Currency.objects.get(id=int(data["currency"]))
        amount = float(tour_request.price) * float(currency.sell) - float(tour_request.paid)

        transaction = Transaction.objects.create(
            status="processing",
            name="tour",
            tour_id=tour_request.id,
            user=user,
            amount=amount,
            rid=Transaction.generate_unique_code(),
        )

        tour_request.payler_url = f"https://sandbox.payler.com/gapi/Pay?session_id={transaction.id}"
        tour_request.transaction_id = transaction.id
        tour_request.save()

        deeplink = f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={int(transaction.amount)}"
        return transaction, deeplink
    except Exception:
        return None, None


def decrease_user_bonuses(user, bonuses):
    """Уменьшение бонусов пользователя."""
    try:
        decrease_bonuses(user.bcard_id, bonuses, "test")
        return True
    except Exception:
        return False


def create_hotel_service(request_number, data=None):
    """Создание заявки на отель в системе Uon."""
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

    requests.post(f"https://api.u-on.ru/{KEY}/service/create.json", data=uon_data)


def add_tourist(travelers):
    """Добавление туристов в систему Uon."""
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


def determine_u_tk_id(u_birthday):
    """Определение ID группы туриста в системе Uon на основе возраста."""
    if not u_birthday:
        return None

    birth_date = datetime.strptime(u_birthday, "%Y-%m-%d")
    age = (datetime.now() - birth_date).days // 365

    if age >= 18:
        return 1
    elif 12 <= age < 18:
        return 3
    elif 2 <= age < 12:
        return 4
    else:
        return 5


def hotel_lead(data, user):
    """Создание заявки на отель и добавление туристов."""
    url = f"https://api.u-on.ru/{KEY}/request/create.json"
    note = f"Заявки на отель №{data['hotelid']}"

    r_data = {
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
        u_birthday = traveler.get("dateofborn")
        u_tk_id = determine_u_tk_id(u_birthday)

        r_data["tourists"].append({
            "u_tk_id": u_tk_id,
            "u_zagran_number": traveler.get("passport_id"),
            "u_zagran_given": traveler.get("issued_by"),
            "u_name": traveler.get("first_name"),
            "u_surname": traveler.get("last_name"),
            "u_birthday": u_birthday,
        })

    response = requests.post(url, json=r_data)

    if response.status_code == 200:
        response_data = response.json()
        create_hotel_service(response_data["id"], data=data)
        add_tourist(travelers)
        return True
    else:
        return False
