import requests
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage

from config.celery import app
from src.account.models import ManualRequests, User
from src.helpers.send_sms import send_sms


def generate_password():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    from os import urandom
    return "".join(chars[c % len(chars)] for c in urandom(8))

def send_email(data):
    email = EmailMessage(
        subject=data['email_subject'],
        body=data['email_body'],
        to=[data['to_email']]
    )
    email.content_subtype = "html"
    email.send()

KEY = settings.KEY


@app.task(ignore_result=True)
def add_request(request_id):
    print("Call function")

    url = f"https://api.u-on.ru/{settings.KEY}/request/{request_id}.json"
    print(url)
    res = requests.get(url)

    if res.status_code != 200:
        print(f"Ответ запроса != 200: {res.status_code}")
        return {"response": False, "message": f"Ответ запроса != 200 ({res.status_code})"}

    data = res.json().get("request", [])
    if not data:
        print("Данные запроса пусты")
        return {"response": False, "message": "Данные запроса пусты"}

    data = data[0]
    '''Процесс с юзеркой'''

    user = None
    client_email = data.get("client_email")
    client_phone = data.get("client_phone_mobile")
    client_phone = "".join(filter(str.isdigit, client_phone))
    if client_email:
        try:
            user = User.objects.get(email=client_email)
        except ObjectDoesNotExist:
            pass

    if user is None:
        if client_phone and client_phone.startswith("996") and len(client_phone) == 12:
            generated_email = f"{client_phone}@hittravel.com"
            password = generate_password()
            try:
                user = User.objects.get(email=generated_email)
            except ObjectDoesNotExist:
                user = User.objects.create(
                    email=generated_email,
                    password=password,
                    first_name=data["client_name"],
                    last_name=data["client_sname"],
                    is_verified=True,
                    phone=client_phone,
                    gender="н",
                )
                user.set_password(password)
                user.save()

                sms_text = (
                    f"Ваш аккаунт был автоматически создан. "
                    f"Логин: {generated_email}, Пароль: {password}"
                )
                try:
                    send_sms(client_phone, sms_text)
                except Exception as e:
                    print(f"Error sending SMS: {e}")

        else:
            print("Не указан email клиента и недопустимый номер телефона")
            return {"response": False, "message": "Не указан email клиента и недопустимый номер телефона"}

    # If user was found or successfully created, check existing request
    ManualRequests.objects.create(user=user, request_id=request_id)
    # try:
    #     if RequestTour.objects.filter(user=user, request_number=data["id"]).exists():
    #         return False
    # except Exception as e:
    #     print(f"Nice")

    # obj = RequestTour.objects.create(
    #     user=user,
    #     status=1,
    #     first_name=data["client_name"],
    #     last_name=data["client_surname"],
    #     phone=data["client_phone_mobile"],
    #     email=data["client_email"],
    #     gender="",
    #     dateofborn="2022-12-12",
    #     inn=data["client_inn"],
    #     passport_id="",
    #     date_of_issue="2020-12-12",
    #     issued_by="1",
    #     validity="2020-12-12",
    #     tourid="0",
    #     operatorlink="https://hit-travel.org",
    #     request_number=request_id,
    #     from_main_view=False,
    # )
    # print("Created RequestTour object")

    # if data["tourists"]:
    #     for i in data["tourists"]:
    #         birthday_str = i["u_birthday"]
    #         date_of_birth = datetime.strptime(birthday_str, "%Y-%m-%d %H:%M")
            
    #         tourist = Traveler.objects.create(
    #             first_name=i["u_name"],
    #             last_name=i["u_surname"],
    #             dateofborn=date_of_birth,
    #             passport_id=i["u_zagran_number"],
    #             issued_by=i["u_zagran_organization"],
    #             main=obj
    #         )
    #         print(f"Created Traveler object: {tourist.first_name} {tourist.last_name}")

    # request_tour_service = RequestTourService.objects.create(
    #     main=obj,
    #     tour_name=data["travel_type"],
    #     manager_name=f"{data['manager_surname']} {data['manager_name']} {data['manager_sname']}",
    #     office_name=data["office_name"],
    #     date_begin=data["date_begin"],
    #     date_end=data["date_end"],
    #     status_pay_name=data["status_pay_name"],
    #     company_name=data["company_name"],
    #     client_requirements_country_names=data["client_requirements_country_names"]
    # )
    # print("Created RequestTourService object")

    # if data["services"]:
    #     for service in data["services"]:
    #         if service.get("service_type") == "Пакетный тур":
    #             request_tour_service.t_service_type = service.get("service_type")
    #             request_tour_service.t_partner_name = service.get("date_begin")
    #             request_tour_service.t_date_begin = service.get("date_begin")
    #             request_tour_service.t_date_end = service.get("date_end")
    #             request_tour_service.t_price_netto = service.get("price_netto")
    #             request_tour_service.t_currency = service.get("currency_netto")
    #             request_tour_service.t_tourists_count = service.get("tourists_count")
    #             request_tour_service.t_tourists_child_count = service.get("tourists_child_count")
    #             request_tour_service.t_tourists_baby_count = service.get("tourists_baby_count")
    #             request_tour_service.t_hotel_place_id = service.get("hotel_place_id")
    #             request_tour_service.t_hotel_place = service.get("hotel_place")
    #             request_tour_service.have_tour=True

    #         if service.get("service_type") == "Отель":
    #             request_tour_service.h_service_type = service.get("service_type")
    #             request_tour_service.h_date_begin = service.get("date_begin")
    #             request_tour_service.h_date_end = service.get("date_end")
    #             request_tour_service.h_hotel = service.get("hotel")
    #             request_tour_service.h_hotel_place_id = service.get("hotel_place_id")
    #             request_tour_service.h_hotel_place = service.get("hotel_place")
    #             request_tour_service.have_hotel=True

    #         if service.get("service_type") == "Страховка":
    #             request_tour_service.i_service_type = service.get("service_type")
    #             request_tour_service.i_partner_name = service.get("partner_name")
    #             request_tour_service.i_date_begin = service.get("date_begin")
    #             request_tour_service.i_date_end = service.get("date_end")
    #             request_tour_service.i_price_netto = service.get("price_netto")
    #             request_tour_service.i_currency = service.get("currency_netto")
    #             request_tour_service.have_insurance=True

    #         if service.get("service_type") == "Трансфер":
    #             request_tour_service.tr_service_type = service.get("service_type")
    #             request_tour_service.tr_partner_name = service.get("partner_name")
    #             request_tour_service.tr_date_begin = service.get("date_begin")
    #             request_tour_service.tr_date_end = service.get("date_end")
    #             request_tour_service.tr_course = service.get("course")
    #             request_tour_service.tr_price_netto = service.get("price_netto")
    #             request_tour_service.tr_currency = service.get("currency_netto")
    #             request_tour_service.have_transfer=True

    #         if service.get("service_type") == "Авиабилет":
    #             request_tour_service.a_main = service.get("service_type")
    #             request_tour_service.a_description = service.get("description")
    #             request_tour_service.a_partner_name = service.get("partner_name")
    #             request_tour_service.have_avia=True
    #             for flight_data in service["flights"]:
    #                 flight, created = Flight.objects.get_or_create(
    #                     date_begin=flight_data.get("date_begin"),
    #                     time_begin=flight_data.get("time_begin"),
    #                     date_end=flight_data.get("date_end"),
    #                     time_end=flight_data.get("time_end"),
    #                     flight_number=flight_data.get("flight_number"),
    #                     course_begin=flight_data.get("course_begin"),
    #                     course_end=flight_data.get("course_end"),
    #                     terminal_begin=flight_data.get("terminal_begin"),
    #                     terminal_end=flight_data.get("terminal_end"),
    #                     code_begin=flight_data.get("code_begin"),
    #                     code_end=flight_data.get("code_end"),
    #                     seats=flight_data.get("seats"),
    #                     tickets=flight_data.get("tickets"),
    #                     type=flight_data.get("type"),
    #                     flight_class=flight_data.get("flight_class"),
    #                     duration=flight_data.get("duration"),
    #                     baggage=flight_data.get("baggage"),
    #                     supplier_id=flight_data.get("supplier_id"),
    #                     supplier_name=flight_data.get("supplier_name"),
    #                 )
    #                 request_tour_service.a_flights.add(flight)

    # request_tour_service.save()
    print("Saved RequestTourService object")
    print("DONE")


def add_client(sender, instance):
    url = f"https://api.u-on.ru/RxH3WeM378er81w4dMuF1649063416/user/{instance.request_id}.json"