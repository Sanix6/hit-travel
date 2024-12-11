import requests
from datetime import datetime
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
import json
from django.conf import settings
from .models import RequestTour, RequestHotel
from .serializers import TourRequestSerializer, RequestHotelSerializer, PersonalInfoSerializer
from .services import create_lead, decrease_bonuses
from .functions import hotel_lead, create_hotel_service
from django.core.files.base import ContentFile
from django.template.loader import get_template
import pdfkit
from num2words import num2words
from src.payment.models import Transaction
from src.main.models import Currency


class TourRequestView(generics.CreateAPIView):
    serializer_class = TourRequestSerializer
    queryset = RequestTour.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user = request.user

        if serializer.is_valid():
            tour_id = serializer.validated_data.get("tourid")
            existing_tour_request = RequestTour.objects.filter(
                tourid=tour_id, user=user
            )

            if existing_tour_request.exists():
                return Response({"response": False})

            serializer.save(user=request.user)
            
            res = create_lead(serializer.data, user)
            if res:
                tour_request = RequestTour.objects.get(tourid=tour_id, user=user)
                tour_request.request_number = res["id"]

                date = datetime.now().strftime("%d.%m.%Y %H:%M")
                price_word = num2words(float(tour_request.price), lang="ru")
                surcharge_word = num2words(int(tour_request.surcharge), lang="ru")

                tour = requests.get(f"https://hit-travel.org/api/detail/tour/{tour_id}")

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

                tour_request.paid = float(serializer.data["bonuses"])
                tour_request.save()
                bonuses = decrease_bonuses(
                    user.bcard_id, serializer.data["bonuses"], "test"
                )
                amount = float(tour_request.price) * float(Currency.objects.get(id=int(serializer.data["currency"])).sell) - float(tour_request.paid)
                transaction = Transaction.objects.create(
                    status="processing",
                    name="tour",
                    tour_id=tour_request.id,
                    user=request.user,
                    amount=amount,
                    rid=Transaction.generate_unique_code()
                    )
                tour_request.payler_url = f"https://sandbox.payler.com/gapi/Pay?session_id={transaction.id}"
                tour_request.transaction_id = transaction.id
                tour_request.save()
                deeplink = f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={int(transaction.amount)}"

                return Response(
                    {
                        "response": True,
                        "message": "Заявка успешно отправлено",
                        "deeplink": deeplink,
                        "amount": transaction.amount,
                        "data": TourRequestSerializer(RequestTour.objects.get(id=tour_request.id)).data,
                        "transaction_id": transaction.id,
                    }
                )
            return Response(serializer.errors)


class RequestHotelView(views.APIView):
    authlogin = settings.AUTHLOGIN
    authpass = settings.AUTHPASS
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = RequestHotelSerializer(data=request.data)
        if serializer.is_valid():
            price_netto = serializer.validated_data["price"]
            price = price_netto * float(Currency.objects.first().sell)
            
            nights = serializer.validated_data.get("nights")
            flydate = serializer.validated_data.get("flydate")
            placement = serializer.validated_data.get("placement")
            adults = serializer.validated_data.get("adults", 1)
            child = serializer.validated_data.get("child", 0)
            mealcode = serializer.validated_data.get("mealcode")
            mealrussian = serializer.validated_data.get("mealrussian")
            meal = serializer.validated_data.get("meal")
            
            instance = serializer.save(
                user=request.user,
                price=price,
                price_netto=price_netto,
                nights=nights,
                flydate=flydate,
                placement=placement,
                adults=adults,
                child=child,
                mealcode=mealcode,
                mealrussian=mealrussian,
                meal=meal
            )
            
            hotel_lead(serializer.data, request.user)
            
            transaction = Transaction.objects.create(
                status="processing",
                name="hotel",
                hotel_id=instance.id,
                user=request.user,
                amount=price,
                rid=Transaction.generate_unique_code()
            )
            
            instance.payler_url = f"https://sandbox.payler.com/gapi/Pay?session_id={transaction.id}"
            instance.transaction_id = transaction.id
            instance.save()
            
            deeplink = f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={int(price)}"
            
            return Response({
                "response": True,
                "deeplink": deeplink,
                "amount": transaction.amount,
                "data": RequestHotelSerializer(instance).data,
                "transaction_id": transaction.id,
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request, format=None):
        user_requests = RequestHotel.objects.filter(user=request.user).order_by("-id")
        serializer = RequestHotelSerializer(user_requests, many=True, context={"type": "list"})
        combined_data = []

        for item in serializer.data:
            url = f"http://tourvisor.ru/xml/hotel.php?format=json&authlogin={self.authlogin}&authpass={self.authpass}&hotelcode={item['hotelid']}"
            response = requests.get(url)
            if response.status_code == 200:
                data_from_url = response.json()
                combined_entry = {**item, **data_from_url}
                combined_data.append(combined_entry)

        return Response(combined_data)




class HotelDetail(views.APIView):
    authlogin = settings.AUTHLOGIN
    authpass = settings.AUTHPASS

    def get(self, request, pk, format=None):
        request_hotel = generics.get_object_or_404(RequestHotel, pk=pk)
        serializer = RequestHotelSerializer(request_hotel, context={"type": "detail", "id": pk})
        hotelcode = serializer.data.get('hotelcode')
        url = f"http://tourvisor.ru/xml/hotel.php?format=json&authlogin={self.authlogin}&authpass={self.authpass}&hotelcode={hotelcode}"

        response = requests.get(url)
        
        if response.status_code == 200:
            data_from_database = serializer.data
            data_from_url = response.json()
            combined_data = {}
            combined_data.update(data_from_database)
            combined_data.update(data_from_url)
            combined_data["user"] = PersonalInfoSerializer(request_hotel.user, context={"request": request}).data
            
            return Response(combined_data)
        else:
            return Response({"error": "Ошибка при получении данных отеля"}, status=response.status_code)
        

