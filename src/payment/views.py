import logging
import xml.etree.ElementTree as ET
from datetime import datetime
from xml.etree.ElementTree import ParseError

import redis
import requests
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.views import APIView

from src.account.models import RequestHotel, RequestTour
from src.flights.models import FlightRequest
from src.flights.services import ticketed
from src.payment.models import Transaction

from .serializers import TransactionSerializer


class MPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        datetime_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            root = ET.fromstring(request.body)
            xml_body = root.find("BODY")
            xml_head = root.find("HEAD")
            qm = xml_head.get("QM")
            qid = xml_head.get("QID")
            op = xml_head.get("OP")

            if qm != "MOB":
                return self.error_response(
                    datetime_now, qid, "401", "Некорректное значение QM"
                )

            if op == "QE10":  # ConfirmPaymentView
                return self.confirm_payment(xml_body, xml_head, datetime_now)

            elif op == "QE11":  # CheckPaymentView
                return self.check_payment(xml_body, xml_head, datetime_now)

            else:
                return self.error_response(
                    datetime_now, qid, "401", "Некорректное значение OP"
                )

        except ParseError:
            return self.error_response(
                datetime_now, None, "401", "Некорректный формат данных"
            )

        except Exception as e:
            logging.error(e)
            return self.error_response(
                datetime_now, None, "424", "Сервис временно недоступен"
            )

    def confirm_payment(self, xml_body, xml_head, datetime_now):
        qid = xml_head.get("QID")
        try:
            redis_client = redis.StrictRedis(host="localhost", port=6379, db=1)
            token = redis_client.get("token").decode("utf-8")
            transaction = Transaction.objects.get(rid=xml_body.get("PARAM1"))
            if (
                transaction.amount == float(xml_body.get("SUM"))
                and transaction.status == "processing"
            ):

                if transaction.name == "ticket":
                    flight_request = FlightRequest.objects.get(
                        id=transaction.request_id
                    )
                    ticketed(token, flight_request)
                    flight_request.status = "ticketed"
                    flight_request.save()

                if transaction.name == "tour":
                    from src.account.services import create_lead

                    tour_request = RequestTour.objects.get(id=transaction.tour_id)
                    tour_request.status = 3
                    res = create_lead(tour_request, flight_request.user)
                    if res:
                        tour_requestrequest_number = res["id"]
                    tour_request.save()

                if transaction.name == "hotel":
                    hotel_request = RequestHotel.objects.get(id=transaction.hotel_id)
                    hotel_request.status = 3
                    hotel_request.save()

                transaction.status = "completed"
                transaction.qid = qid
                transaction.save()

                response_data = f"""<?xml version="1.0" encoding="utf-8"?><XML><HEAD DTS="{datetime_now}" QM="MOB" QID="{qid}" OP="QE10" /><BODY STATUS="250" MSG="Платеж успешно проведен" /></XML>"""

                # Logging
                self.log_data(datetime_now, self.request.body, response_data)

                return HttpResponse(response_data, content_type="application/xml")

            elif transaction.amount > float(xml_body.get("SUM")):
                return self.error_response(
                    datetime_now,
                    qid,
                    "423",
                    "Заявленная сумма платежа меньше стоимости услуги",
                )

            elif transaction.amount < float(xml_body.get("SUM")):
                return self.error_response(
                    datetime_now,
                    qid,
                    "422",
                    "Заявленная сумма платежа превышает стоимость услуги",
                )

        except Transaction.DoesNotExist:
            return self.error_response(
                datetime_now, qid, "420", "Лицевой счет не найден"
            )

    def check_payment(self, xml_body, xml_head, datetime_now):
        qid = xml_head.get("QID")
        try:
            if Transaction.objects.filter(qid=qid).exists():
                return self.error_response(
                    datetime_now, qid, "421", "Дублирование платежа"
                )

            transaction = Transaction.objects.get(rid=xml_body.get("PARAM1"))
            if transaction.name == "ticket":
                flight_request = FlightRequest.objects.get(id=transaction.request_id)
                res_requisite = "Авиабилеты"

            if transaction.name == "tour":
                flight_request = RequestTour.objects.get(id=transaction.request_id)
                res_requisite = "Туры"

            response_data = f"""<?xml version="1.0" encoding="utf-8"?><XML><HEAD DTS="{datetime_now}" QM="MOB" OP="QE11" /><BODY STATUS="200" MSG="Проверка прошла успешно" SUM="{transaction.amount:.2f}" REQUISITE1="ФИО: {flight_request.user.first_name} {flight_request.user.last_name}" REQUISITE2="Hit-Travel: {res_requisite}"/></XML>"""

            self.log_data(datetime_now, self.request.body, response_data)

            return HttpResponse(response_data, content_type="application/xml")

        except Transaction.DoesNotExist:
            return self.error_response(datetime_now, qid, "420", "Объект не найден")

    def error_response(self, datetime_now, qid, status, err_msg):
        response_data = f"""<?xml version="1.0" encoding="utf-8"?><XML><HEAD DTS="{datetime_now}" QM="MOB" QID="{qid}" OP="QE10" /><BODY STATUS="{status}" ERR_MSG="{err_msg}" /></XML>"""

        self.log_data(datetime_now, self.request.body, response_data)

        return HttpResponse(response_data, content_type="application/xml")

    def log_data(self, datetime_now, request_body, response_data):
        log_line = f"Date: {datetime_now}, Request Body: {request_body}, Response Data: {response_data}\n"
        with open("mbank.log", "a") as f:
            f.write(log_line)


class PaylerPaymentView(APIView):

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            try:
                transaction = Transaction.objects.get(
                    id=serializer.data.get("order_id"),
                    user=request.user,
                    status="processing",
                )
            except Exception as e:
                return Response({"response": False, "message": f"{e}"})

            url = "https://sandbox.payler.com/gapi/StartSession"
            data = {
                "key": settings.PAYLER_API_KEY,
                "type": "OneStep",
                "order_id": f"{transaction.id}",
                "amount": int(transaction.amount * 100),
                "currency": "KGS",
                "product": f"{transaction.name}",
                "lang": "ru",
                "email": f"{transaction.user.email}",
                "return_url_success": f"https://hit-travel.org/payler/check/?order_id={transaction.id}",
            }

            response = requests.post(url, data=data)
            response_data = response.json()

            if response.status_code != 200:
                return Response(
                    {"response": False, "message": response_data["error"]["message"]}
                )

            session_id = f"https://sandbox.payler.com/gapi/Pay?session_id={response_data['session_id']}"

            if transaction.name == "tour":
                tour = RequestTour.objects.get(id=transaction.tour_id)
                tour.payler_url = session_id
                tour.save()
            if transaction.name == "hotel":
                hotel = RequestHotel.objects.get(id=transaction.hotel_id)
                hotel.payler_url = session_id
                hotel.save()
            if transaction.name == "ticket":
                hotel = FlightRequest.objects.get(id=transaction.request_id)
                hotel.payler_url = session_id
                hotel.save()

            # model_mapping = {
            #     "tour": RequestTour,
            #     "hotel": RequestHotel,
            #     "ticket": FlightRequest
            # }

            # if transaction.name in model_mapping:
            #     model = model_mapping[transaction.name]
            #     instance = model.objects.get(id=getattr(transaction, f"{transaction.name}_id"))
            #     instance.payler_url = session_id
            #     instance.save()

            response_data["url"] = session_id

            return Response(response_data)
        return Response(serializer.errors, status=400)


class PaylerCallbackView(APIView):
    def post(self, request):
        order_id = self.request.query_params.get("order_id")
        print(order_id)
        try:
            transaction = Transaction.objects.get(id=order_id, status="processing")
        except Transaction.DoesNotExist:
            return Response(
                {"response": True, "message": "Не удалось найти счет."}, status=404
            )
        except Exception as e:
            return Response({"response": True, "message": f"{e}"}, status=400)

        url = "https://sandbox.payler.com/gapi/GetStatus"
        body = {
            "key": settings.PAYLER_API_KEY,
            "order_id": order_id,
        }
        response = requests.post(url, data=body)

        if response.status_code != 200:
            return Response(
                {"response": True, "message": f'{response.json()["error"]["message"]}'}
            )

        response = response.json()
        if response.get("status") == "Charged":
            if transaction.name == "ticket":
                flight_request = FlightRequest.objects.get(id=transaction.request_id)
                redis_client = redis.StrictRedis(host="localhost", port=6379, db=1)
                token = redis_client.get("token").decode("utf-8")
                ticketed(token, flight_request)
                flight_request.status = "ticketed"
                flight_request.save()

            elif transaction.name == "tour":
                from src.account.services import create_lead

                tour_request = RequestTour.objects.get(id=transaction.tour_id)
                tour_request.status = 3
                res = create_lead(tour_request, tour_request.user)
                if res:
                    tour_requestrequest_number = res["id"]
                tour_request.save()

            elif transaction.name == "hotel":
                hotel_request = RequestHotel.objects.get(id=transaction.hotel_id)
                hotel_request.status = 3
                hotel_request.save()

            else:
                return Response(
                    {"response": False, "message": "Invalid transaction name."},
                    status=400,
                )

            transaction.status = "completed"
            transaction.save()

            return Response(
                {
                    "response": True,
                    "message": "Продукт куплен, можете перейти на приложение)",
                }
            )
        else:
            return Response({"response": False, "message": "Ошибка в процессе."})


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class PaymentCallbackFront(TemplateView):
    template_name = "payments/payment_check.html"


# class PaylerReturnView(APIView):
#     def get(self, request):
#         data = request.GET
#         try:
#             transaction = Transaction.objects.get(rid=data['order_id'])
#             context = {'transaction': transaction}
#             if data['status'] == 'success':
#                 transaction.status = 'completed'
#                 transaction.save()
#                 return render(request, 'payments/success.html', context)
#             else:
#                 transaction.status = 'failed'
#                 transaction.save()
#                 return render(request, 'payments/failure.html', context)
#         except Transaction.DoesNotExist:
#             return render(request, 'payments/error.html', {'error': 'Transaction not found'})
