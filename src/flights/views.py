# Standard library imports
import json
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from urllib.parse import urlencode
from config.celery import get_token

import redis
import requests

# Django imports
from django.conf import settings
from rest_framework.generics import GenericAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from redis import ConnectionPool


# Third-party imports
from rest_framework.response import Response
from rest_framework.views import APIView

# Application-specific imports
from src.flights.models import FlightCancel, FlightRequest, Passengers, Segments
from src.flights.serializers import (
    CancelBookingSerializer,
    FlightsSerializer,
    RefundAmountSerializer,
)
from src.flights.services import booking, create_request
from src.flights.tasks import *
from src.payment.models import Transaction

from .functions import *
from .services import *
from django.shortcuts import get_object_or_404
from django.db import transaction

avia_center_url = settings.AVIA_URL
pool = ConnectionPool(host='localhost', port=6379, db=0)
redis_client = redis.StrictRedis(connection_pool=pool)


class SearchParamsViewV3(APIView):
    def get(self, request):
        file_path = f"src/flights/avia.json"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                data = json.load(file)
            return Response(data)
        except FileNotFoundError:
            return Response(
                {"response": False, "message": "File not found"}, status=404
            )


class SearchParamsView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
            token = redis_client.get("token").decode("utf-8")
        except Exception as e:
            return Response(
                {"message": "Failed to connect to Redis or retrieve token"}, status=500
            )

        city = self.kwargs.get("city", "")
        url = f"{avia_center_url}/avia/airports?&auth_key={token}&lang=ru&part={city}"
        response = requests.get(url.encode("utf-8")).json().get("data")

        cities_list = [value for key, value in response["cities"].items()]
        response["cities"] = cities_list
        return Response(response)

        
class FlightsSearchView(APIView):
    def get(self, request):
        try:
            redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)
            token = redis_client.get('token').decode("utf-8")
        except Exception as e:
            return Response({"message": "Failed to connect to Redis or retrieve token"}, status=500)

        avia_center_url = settings.AVIA_URL
        encoded_params = urlencode(request.query_params, safe='[]')
        url = f"{avia_center_url}/avia/search-recommendations?auth_key={token}&{encoded_params}"
        response = requests.get(url.encode("utf-8"))
        response_data = response.json().get("data", {})

        is_refund_filter = request.query_params.get('is_refund', 'false').lower() == 'true'
        is_baggage_filter = request.query_params.get('is_baggage', 'false').lower() == 'true'

        flights = response_data.get('flights', [])
        filtered_flights = filter_flights(flights, is_refund_filter, is_baggage_filter)

        flight_date = datetime.strptime(request.query_params.get('segments[0][date]'), '%d.%m.%Y')
        offsets = range(-2, 3)

        with ThreadPoolExecutor() as executor:
            nearest_flights = list(filter(None, executor.map(
                lambda offset: fetch_nearest_flights(offset, avia_center_url, token, request.query_params, flight_date),
                offsets
            )))

        nearest_flights_formatted = format_nearest_flights(nearest_flights, flight_date)

        response_data['flights'] = filtered_flights
        response_data['nearest'] = nearest_flights_formatted

        return Response(response_data)


class FlightDetailView(APIView):
    def get(self, request, *args, **kwargs):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        token = redis_client.get("token").decode("utf-8")
        url = f"{avia_center_url}/avia/flight-info?auth_key={token}"
        url += f"&tid={self.kwargs['tid']}"
        response = requests.get(url.encode("utf-8"))
        response_data = {}
        response_data.update(response.json()["data"])
        return Response(response_data)


class FlightRulesView(APIView):
    """Agreement"""

    def get(self, request, *args, **kwargs):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        token = redis_client.get("token").decode("utf-8")
        url = f"{avia_center_url}/avia/rules?auth_key={token}"
        url += f"&tid={self.kwargs['tid']}"
        response = requests.get(url.encode("utf-8"))
        response_data = {}
        response_data.update(response.json()["data"])
        return Response(response_data)


class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        token = redis_client.get("token").decode("utf-8")
        parameters = request.query_params

        tid = parameters.get("tid")
        encoded_url = urlencode(parameters)

        existing_request = FlightRequest.objects.filter(
            tid=tid,
            status='booked'
        ).first()

        if existing_request:
            return Response({
                "error": "Этот билет уже забронирован. Дождитесь завершения оплаты или отмените бронирование.",
                "flight_request_id": existing_request.id,
                "status": existing_request.status,
            }, status=400)

        flight_detail_url = f"{avia_center_url}/avia/flight-info?auth_key={token}&tid={tid}"
        flight_detail = requests.get(flight_detail_url).json()

        segments = flight_detail.get("data", {}).get("search", {}).get("segments", [])
        segments_date = flight_detail.get("data", {}).get("flight", {}).get("segments", [])
        partner_affiliate_fee = (
            flight_detail.get("data", {})
            .get("flight", {})
            .get("price", {})
            .get("KGS", {})
            .get("agent_mode_prices", {})
            .get("total_partner_affiliate_fee", 0)
        )

        flight_request = FlightRequest.objects.create(
            url=encoded_url,
            tid=tid,
            user=request.user,
            client_email=parameters.get("client_email"),
            client_phone=parameters.get("client_phone"),
            payer_name=parameters.get("payer_name"),
            amount=flight_detail["data"]["flight"]["price"]["KGS"]["amount"],
            book_class=flight_detail["data"]["search"]["class"].lower(),
            type=flight_detail["data"]["flight"]["type"],
            is_baggage=flight_detail["data"]["flight"]["is_baggage"],
            provider=flight_detail["data"]["flight"]["provider"]["supplier"]["title"],
            code=flight_detail["data"]["flight"]["provider"]["supplier"]["code"],
            flight_number=flight_detail["data"]["flight"]["segments"][0]["flight_number"],
            adt=flight_detail["data"]["search"]["adt"],
            chd=flight_detail["data"]["search"]["chd"],
            inf=flight_detail["data"]["search"]["adt"],
            partner_affiliate_fee=partner_affiliate_fee,
        )

        count = int(parameters.get("count", 0))
        for i in range(count):
            birthdate = parameters.get(f"passengers[{i}][birthdate]")
            docexp = parameters.get(f"passengers[{i}][docexp]")

            passenger_data = {
                "first_name": parameters.get(f"passengers[{i}][firstname]"),
                "last_name": parameters.get(f"passengers[{i}][lastname]"),
                "middlename": parameters.get(f"passengers[{i}][middlename]"),
                "age": parameters.get(f"passengers[{i}][age]"),
                "birthdate": (
                    datetime.strptime(birthdate, "%d.%m.%Y").strftime("%Y-%m-%d")
                    if birthdate else None
                ),
                "doctype": parameters.get(f"passengers[{i}][doctype]"),
                "docnum": parameters.get(f"passengers[{i}][docnum]"),
                "docexp": (
                    datetime.strptime(docexp, "%d.%m.%Y").strftime("%Y-%m-%d")
                    if docexp else None
                ),
                "gender": parameters.get(f"passengers[{i}][gender]"),
                "citizen": parameters.get(f"passengers[{i}][citizen]"),
                "phone": parameters.get(f"passengers[{i}][phone]"),
                "email": parameters.get(f"passengers[{i}][email]"),
            }
            Passengers.objects.create(main=flight_request, **passenger_data)

        for segment_data, date_data in zip(segments, segments_date):
            Segments.objects.create(
                main=flight_request,
                from_name=segment_data.get("from", {}).get("name", ""),
                from_iata=segment_data.get("from", {}).get("iata", ""),
                from_country=segment_data.get("from", {}).get("country", {}).get("name", ""),
                to_name=segment_data.get("to", {}).get("name", ""),
                to_iata=segment_data.get("to", {}).get("iata", ""),
                to_country=segment_data.get("to", {}).get("country", {}).get("name", ""),
                date_from=date_data.get("dep", {}).get("date"),
                date_to=date_data.get("arr", {}).get("date"),
                time_from=date_data.get("dep", {}).get("time"),
                time_to=date_data.get("arr", {}).get("time"),
                duration_hour=date_data.get("duration", {}).get("flight", {}).get("hour"),
                duration_minute=date_data.get("duration", {}).get("flight", {}).get("minute"),
            )

        amount = flight_detail["data"]["flight"]["price"]["KGS"]["amount"]
        transaction = Transaction.objects.create(
            status="processing",
            name="ticket",
            request_id=str(flight_request.id),
            user=request.user,
            amount=amount,
            rid=Transaction.generate_unique_code(),
        )

        flight_request.payler_url = f"https://sandbox.payler.com/gapi/Pay?session_id={transaction.id}"
        flight_request.transaction_id = transaction.id
        flight_request.save()

        deeplink = f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={amount}"

        booking_result = booking(token, flight_request.url, flight_request.id)
        flight_request.refresh_from_db()

        if booking_result is True:
            create_request(data=flight_request, user=request.user)
            return Response({
                "response": True,
                "deeplink": deeplink,
                "amount": amount,
                "data": FlightsSerializer(flight_request, context={"request_type": None}).data,
                "adt": flight_request.adt,
                "transaction_id": transaction.id,
            })
        else:
            transaction.delete()
            flight_request.delete()
            return Response({"message": booking_result.replace("\n", "")})


class BookingHistory(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FlightsSerializer

    def get_queryset(self):
        return FlightRequest.objects.filter(
            user=self.request.user, status__in=["booked", "canceled", "ticketed"]
        ).order_by("-created_at")

    def get(self, request, *args, **kwargs):
        serializer_context = {"request_type": "list"}
        return Response(
            self.get_serializer(
                self.get_queryset(), many=True, context=serializer_context
            ).data
        )


class BookingHistoryDetail(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FlightsSerializer

    def get(self, request, *args, **kwargs):
        queryset = FlightRequest.objects.all()
        booking_id = self.kwargs.get("booking_id")
        if booking_id is not None:
            queryset = queryset.get(id=booking_id, user=request.user)
            serializer_context = {"request_type": "detail", "id": booking_id}
            serializer = self.get_serializer(
                queryset, many=False, context=serializer_context
            )
            return Response(serializer.data)


class BookingInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
        token = redis_client.get("token").decode("utf-8")
        billing_number = self.kwargs.get("billing_number")
        url = f"{avia_center_url}/avia/book-info?auth_key={token}&lang=ru&billing_number={billing_number}"
        response = requests.get(url)
        return Response(response.json())


class GetTokenView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            redis_client = redis.StrictRedis(host="localhost", port=6379, db=2)
            token = redis_client.get("cancel_token")

            if token:
                return Response({"token": token.decode("utf-8")}, status=200)
            else:
                get_auth_key.apply_async()
                return Response(
                    {"message": "Токен не найден. Он будет обновлён в фоновом режиме."},
                    status=202,
                )

        except redis.exceptions.ConnectionError as e:
            return Response(
                {"error": f"Ошибка соединения с Redis: {str(e)}"}, status=500
            )


class RefundAmountsView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RefundAmountSerializer

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)

        if serializer.is_valid():
            billing_number = serializer.validated_data.get("billing_number")
            redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
            token = redis_client.get("token")
            token = token.decode("utf-8") if isinstance(token, bytes) else token

            url = f"{avia_center_url}/avia/get-refund-amounts"
            params = {
                "auth_key": token,
                "billing_number": billing_number,
            }
            try:
                response = requests.get(url, params=params)
                if response.status_code == 200:
                    return Response(response.json())
                else:
                    return Response(
                        {
                            "error": "Failed to fetch refund amounts",
                            "details": response.text,
                        },
                        status=response.status_code,
                    )
            except requests.exceptions.RequestException as e:
                return Response({"error": str(e)}, status=500)
        return Response(serializer.errors, status=400)



class CancelBookingView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CancelBookingSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            booking_id = serializer.validated_data.get("booking_id")
            billing_number = serializer.validated_data.get("billing_number")
            redis_client = redis.StrictRedis(host="localhost", port=6379, db=0)
            token = redis_client.get("token")
            token = token.decode("utf-8") if isinstance(token, bytes) else token

            url = f"{avia_center_url}/avia/booking-cancel"
            params = {
                "auth_key": token,
                "billing": billing_number,
            }

            try:
                response = requests.post(url, json=params)
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if response_data.get("success") and response_data.get("data", {}).get("status") == "Cancelled":
                        with transaction.atomic():
                            flight_request = get_object_or_404(FlightRequest, billing_number=billing_number)
                            flight_request.status = "canceled" 
                            flight_request.save()
                        
                        return Response(response_data)
                    else:
                        return Response(
                            {
                                "error": "Cancellation was not successful",
                                "details": response_data,
                            },
                            status=400,
                        )
                else:
                    return Response(
                        {
                            "error": "Failed to fetch refund amounts",
                            "details": response.text,
                        },
                        status=response.status_code,
                    )
            except requests.exceptions.RequestException as e:
                return Response({"error": str(e)}, status=500)
        return Response(serializer.errors, status=400)


class Token(APIView):
    def get(self, request):
        try:
            token = get_redis_token()
            print(f"Полученный токен: {token}") 
        except ConnectionError as e:
            return Response({"message": str(e)}, status=500)