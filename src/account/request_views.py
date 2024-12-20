import requests
from rest_framework import generics, permissions, views, status
from rest_framework.response import Response
from django.conf import settings
from .models import RequestTour, RequestHotel
from .serializers import TourRequestSerializer, RequestHotelSerializer, PersonalInfoSerializer
from .services import create_lead
from .functions import *
from src.payment.models import Transaction
from src.main.models import Currency



class TourRequestView(generics.CreateAPIView):
    serializer_class = TourRequestSerializer
    queryset = RequestTour.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        user = request.user

        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        tour_id = serializer.validated_data.get("tourid")
        if tour_request_exists(tour_id, user):
            return Response({"response": False, "message": "Заявка уже существует"}, status=400)

        tour_request = serializer.save(user=user)

        lead_response = create_lead(serializer.data, user)
        if not lead_response:
            return Response({"response": False, "message": "Ошибка создания лида"}, status=500)

        update_tour_request_with_lead(tour_request, lead_response, serializer.data)

        pdf_generated = generate_and_save_pdf(tour_request, tour_id)
        if not pdf_generated:
            return Response({"response": False, "message": "Ошибка генерации PDF"}, status=500)

        transaction, deeplink = create_transaction(tour_request, serializer.data, user)
        if not transaction:
            return Response({"response": False, "message": "Ошибка создания транзакции"}, status=500)

        bonuses_updated = decrease_user_bonuses(user, serializer.data["bonuses"])
        if not bonuses_updated:
            return Response({"response": False, "message": "Ошибка уменьшения бонусов"}, status=500)

        return Response(
            {
                "response": True,
                "message": "Заявка успешно отправлена",
                "deeplink": deeplink,
                "amount": transaction.amount,
                "data": TourRequestSerializer(tour_request).data,
                "transaction_id": transaction.id,
            }
        )


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
            adults = serializer.validated_data.get("adults", 0)
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
        

