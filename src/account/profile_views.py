import os
import shutil
import requests
from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, RetrieveAPIView
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from .serializers import *
from src.search.services import get_isfavorite
from src.main.models import Currency
from src.payment.models import Transaction

class UpdateProfilePhotoAPIView(APIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = UpdateProfilePhotoSerializer(
            instance=request.user, data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response({"response": True, "message": "Успешно обновлено"})
        return Response({"response": False})


class RemoveProfilePhotoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user

        if user.photo:
            image_path = os.path.join(
                settings.MEDIA_ROOT, f"profile_photos/{user.photo}"
            )
            if os.path.exists(image_path):
                shutil.rmtree(image_path)

            user.photo = "default.png"
            user.save()
            return Response(
                {"response": True, "message": "Фотография профиля удалена."}
            )
        return Response(
            {
                "response": False,
                "messafe": "Нет фотографии профиля, которую можно удалить.",
            }
        )


class ProfileInfoAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
        except ObjectDoesNotExist:
            return Response(
                {"response": False, "detail": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = PersonalInfoSerializer(user, context={"request": request})

        return Response({"response": True, "data": serializer.data})


class UpdateInfoView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = UpdateInfoSerializer(instance=user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"response": True, "message": "Успешно обновлено"})
        return Response({"response": False})


class DeleteProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user.delete()
        return Response({"response": True, "message": "Пользователь успешно удален"})


class MyTourAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS
        user = request.user

        queryset = RequestTour.objects.filter(user=request.user).order_by('-id')
        response = []

        for item in queryset:
            serializer = TourRequestSerializer(item)

            data = serializer.data


            tourid = data["tourid"]
            tourrequest_id = data["id"]
            status = RequestTour.objects.filter(tourid=tourid, user=request.user).first()
            detail = requests.get(
                f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&request=0"
                f"&format=json&authpass={authpass}&authlogin={authlogin}"
            )

            if detail.status_code != 200:
                continue

            try:
                d = {
                    "from_main_view": True,
                    "id": tourrequest_id,
                    "link": f"http://hit-travel.org{data['agreement']}",
                    "tourid": tourid,
                    "status": status.status,
                    "isfavorite": get_isfavorite(user=user, tourid=tourid),
                    "tour": detail.json()["data"]["tour"],
                    "documents": data["documents"],
                }
                response.append(d)
            except KeyError:
                continue

        return Response(response)
        
class MyTourDetailAPIVIew(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS
        user = request.user

        queryset = RequestTour.objects.filter(id=pk, user=request.user).order_by('-id')
        response = []

        for item in queryset:
            serializer = TourRequestSerializer(item)
            data = serializer.data

            tourid = data["tourid"]
            tourrequest_id = data["id"]
            status = RequestTour.objects.get(tourid=tourid, user=request.user)
            detail = requests.get(
                f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&request=0"
                f"&format=json&authpass={authpass}&authlogin={authlogin}"
            )

            if detail.status_code != 200:
                continue

            try:
                d = {}
                d["id"] = tourrequest_id
                d["payler_url"] = data["payler_url"]
                d["transaction_id"] = data["transaction_id"]
                d["first_name"] = data["first_name"]
                d["last_name"] = data["last_name"]
                d["gender"] = 'Мужчина' if data["gender"] == 'м' else 'Женщина'
                d["phone"] = data["phone"]
                d["email"] = data["email"]
                d["country"] = data["country"]
                d["passport_id"] = data["passport_id"]
                try:
                    transaction = Transaction.objects.get(tour_id=tourrequest_id)
                    d["deeplink"] = f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={int(transaction.amount)}"
                    
                except Transaction.DoesNotExist:
                    d["deeplink"] = None
                d["bonus"] = data["bonuses"] if data["bonuses"] is not None else 0
                currency_obj = Currency.objects.get(id=data["currency"])
                d["price"] = int(float(data["price"]) * float(currency_obj.sell))
                d["paid"] = data["paid"]
                d["amount"] = int(transaction.amount)  # Ensure transaction exists
                d["link"] = f"http://hit-travel.org{data['agreement']}"
                d["tourid"] = tourid
                d["status"] = status.status
                d["isfavorite"] = get_isfavorite(user=user, tourid=tourid)
                d["tour"] = detail.json()["data"]["tour"]
                d["documents"] = data["documents"]
                d["travelers"] = data["travelers"]
                try:
                    manager = User.objects.get(pk=data["manager"])
                    d["manager"] = f"{manager.first_name} {manager.last_name}"
                    d["manager_phone"] = manager.phone
                    d["manager_whatsapp"] = f"https://wa.me/{manager.whatsapp}"
                    d["manager_photo"] = f"https://hit-travel.org{manager.photo.url}"
                    response.append(d)
                except User.DoesNotExist:
                    response.append(d)
            except KeyError:
                continue

        return Response(response)
    

class BonusHistoryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
        except ObjectDoesNotExist:
            return Response(
                {"response": False, "detail": "Пользователь не найден"},
                status=status.HTTP_404_NOT_FOUND,
            )

        bonus_history = requests.get(
            f"https://api.u-on.ru/{settings.KEY}/bcard-bonus-by-card/{user.bcard_id}.json"
        )

        if bonus_history.status_code != 200:
            return Response({"response": False})

        data = bonus_history.json()["records"]
        data.reverse()

        return Response(data)


class ManualRequestsView(ListAPIView):
    serializer_class = ManualRequestsSerializer

    def get_queryset(self):
        queryset = ManualRequests.objects.filter(user=self.request.user)
        
        valid_queryset = [
            instance for instance in queryset
            if ManualRequestsSerializer(instance).data
        ]
        
        return valid_queryset
    
    
class ManualRequestsDetailView(RetrieveAPIView):
    serializer_class = ManualRequestsSerializer

    def get_queryset(self):
        return ManualRequests.objects.filter(user=self.request.user, id=self.kwargs.get("pk"))
    

    
# class CreateAgreementPDF(APIView):
#     def get(self, request, tourrequest_id):
#         obj = TourRequest.objects.get(id=tourrequest_id)
#         date = datetime.now().strftime("%d.%m.%Y %H:%M")
#         price_word = num2words(int(obj.price), lang="ru")
#         surcharge_word = num2words(int(obj.surcharge), lang="ru")

#         context = {
#             "obj": obj,
#             "date": date,
#             "price_word": price_word,
#             "surcharge_word": surcharge_word,
#         }

#         template = get_template("index.html")
#         html = template.render(context)

#         pdf = pdfkit.from_string(html, False)

#         filename = f"agreement_pdf_{obj.request_number}.pdf"

#         obj.agreement.save(
#             f"agreement_pdf_{obj.request_number}.pdf", ContentFile(pdf), save=True
#         )

#         return Response({"agreement_url": obj.agreement.url})


class FAQAPIView(ListAPIView):
    queryset = FAQ.objects.all()
    serializer_class = FAQListSerializer
