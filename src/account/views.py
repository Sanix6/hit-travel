import string
from django.shortcuts import render
import requests
from random import randint, choices
from datetime import datetime, timedelta, timezone
from rest_framework import generics, status, permissions, views
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.contrib.auth import authenticate
from django.template.loader import render_to_string

from ..base.utils import Util
from .serializers import *
from .services import get_user_by_phone, bonus_card_create, increase_bonuses
from .functions import *


class PaymentsAPIView(views.APIView):
    def get(self, request):
        payments = Payments.objects.all()
        serializer = PaymentsSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterAPIViewSerializer

    # def add_tourist(self, user):
    #     crm_data = {
    #         "u_surname": user.last_name,
    #         "u_name": user.first_name,
    #         "u_email": user.email,
    #         "u_phone_mobile": user.phone,
    #     }

    #     key = settings.KEY
    #     res = requests.post(
    #         f"https://api.u-on.ru/{key}/user/create.json", data=crm_data
    #     )
    #     res.raise_for_status()
    #     user.tourist_id = res.json()["id"]
    #     user.save()
    #     return

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)

        if User.objects.filter(email=request.data["email"]).exists():
            return Response(
                {
                    "response": False,
                    "message": "Пользователь с таким email уже существует.",
                }
            )
            
        if User.objects.filter(phone=request.data["phone"]).exists():
            return Response(
                {
                    "response": False,
                    "message": "Пользователь с таким телефоном уже существует.",
                }
            )

        """ Register user in system
        """
        if serializer.is_valid():
            email = serializer.data["email"]
            first_name = serializer.data["first_name"]
            last_name = serializer.data["last_name"]
            password = serializer.data["password"]
            confirm_password = serializer.data["confirm_password"]
            phone = serializer.data["phone"]

            if password != confirm_password:
                return Response(
                    {"response": False, "password": _("Пароли не совпадают.")}
                )

            user = User(
                email=email, first_name=first_name, last_name=last_name, phone=phone
            )
            user.set_password(password)
            user.save()
            
            user.is_verified = False
            user.verification_code_time = datetime.now()
            user.verification_code = randint(100_000, 999_999)
            user.save()

            """ Create tourist in https://u-on.ru
            """
            # self.add_tourist(user)

            """ Send verification code to user
            """
            email_body = (
                f"Привет! {user.last_name} {user.first_name}\n\n"
                f"Для подтверждения регистрации в системе введите код ниже:\n\n"
                f"{user.verification_code}"
            )

            email_data = {
                "email_body": email_body,
                "email_subject": "Подтвердите регистрацию",
                "to_email": user.email,
            }

            Util.send_email(email_data)

            # Get manager_id and touris_id
            # data = get_user_by_phone(user.phone)
            # if data:
            #     user.tourist_id = int(data["u_id"])
            #     user.manager_id = int(data["manager_id"])
            #     user.save()

            # Create bonus card
            # b_card = bonus_card_create(user)
            add_bonuses = increase_bonuses(user.bcard_id, 1000, "Бонус за регистрацию")
            return Response({"response": True}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors)


class VerifyEmailAPIView(generics.GenericAPIView):
    serializer_class = VerifyEmailSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            code = serializer.data["code"]
            email = serializer.data["email"]

            try:
                user = User.objects.get(email=email)

                if user.is_verified:
                    return Response({"message": _("Аккаунт уже подтвержден")})

                if user.verification_code_time:
                    expiration_time = user.verification_code_time + timedelta(
                        minutes=30
                    )
                    expiration_time = expiration_time.replace(tzinfo=timezone.utc)

                    if datetime.now(timezone.utc) >= expiration_time:
                        user.verification_code = None
                        user.verification_code_time = None
                        user.save()
                        return Response(
                            {
                                "reponse": False,
                                "message": _("Срок действия кода истек!"),
                            }
                        )
                    if user.verification_code == code:
                        user.is_verified = True
                        user.save()

                        token, created = Token.objects.get_or_create(user=user)

                        return Response(
                            {
                                "response": True,
                                "message": _("Верификация прошла успешно!"),
                                "token": token.key,
                                "email": user.email,
                            }
                        )
                    return Response(
                        {"response": False, "message": _("Введен неверный код")}
                    )
                return Response(
                    {"response": False, "message": _("Срок действия кода истек!")}
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "response": False,
                        "message": _("Пользователь с таким email не существует"),
                    }
                )
        return Response(
            {"response": False, "detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class SendAgainCodeAPIView(generics.GenericAPIView):
    serializer_class = SendAgainCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            email = serializer.data["email"]

            try:
                user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response(
                    {
                        "reponse": False,
                        "message": _("Пользователь с таким email не существует"),
                    },
                )
            if not user.is_verified:
                user.verification_code = randint(100_000, 999_999)
                user.verification_code_time = datetime.now()
                user.save()

                email_body = f"Ваш новый код активации:\n\n" f"{user.verification_code}"

                email_data = {
                    "email_body": email_body,
                    "email_subject": "Подтвердите регистрацию",
                    "to_email": user.email,
                }

                Util.send_email(email_data)
                return Response(
                    {
                        "response": True,
                        "message": _("Код подтверждения успешно отправлен"),
                    }
                )
            return Response(
                {"response": False, "message": _("Аккаунт уже подтвержден")}
            )
        return Response(
            {"response": False, "detail": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginAPIView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            email = request.data.get("email")
            password = request.data.get("password")

            try:
                get_user = User.objects.get(email=email)
            except ObjectDoesNotExist:
                return Response(
                    {
                        "response": False,
                        "message": "Пользователь с указанными учетными данными не существует",
                    }
                )

            user = authenticate(request, email=email, password=password)

            if not user:
                return Response(
                    {
                        "response": False,
                        "message": "Невозможно войти в систему с указанными учетными данными",
                    }
                )

            if user.is_verified:
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "response": True,
                        "isactivated": True,
                        "token": token.key,
                        "email": user.email,
                    }
                )
            return Response(
                {
                    "response": False,
                    "message": _("Потвердите адрес электронной почты"),
                    "isactivated": False,
                }
            )
        
        return Response(serializer.errors)

    # serializer_class = LoginSerializer

    # def post(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(
    #         data=request.data, context={"request": request}
    #     )
    #     if serializer.is_valid():
    #         try:
    #             user = serializer.validated_data["user"]
    #             email = serializer.validated_data["email"]
    #         except KeyError:
    #             return Response(
    #                 {
    #                     "resonse": False,
    #                     "message": "Невозможно войти в систему с указанными учетными данными",
    #                 }
    #             )
    #         if user.is_verified:
    #             token, created = Token.objects.get_or_create(user=user)
    #             return Response(
    #                 {
    #                     "response": True,
    #                     "isactivated": True,
    #                     "token": token.key,
    #                     "email": user.email,
    #                 }
    #             )
    #         return Response(
    #             {
    #                 "response": False,
    #                 "message": _("Потвердите адрес электронной почты"),
    #                 "isactivated": False,
    #             }
    #         )
    #     return Response(serializer.errors)


class LogoutAPIView(views.APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                token = Token.objects.get(user=user)
                token.delete()
                return Response(
                    {"response": True, "message": _("Выход выполнен успешно")}
                )
            except ObjectDoesNotExist:
                return Response(
                    {"reponse": False, "message": _("Пользователь не авторизован")}
                )
        return Response(
            {"response": False, "message": _("Пользователь не авторизован")}
        )

class PasswordResetRequestAPIView(views.APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            try:
                user = User.objects.get(email=email)
                if user.is_verified:
                    new_password = "".join(
                        choices(string.ascii_letters + string.digits, k=8)
                    )
                    user.set_password(new_password)
                    user.password_reset_token = None  # Ensure token use matches your flow
                    user.save()

                    html_content = render_to_string("password_reset_email.html", {
                        "data": {
                            "name": user.first_name,
                            "email": user.email,
                            "new_password": new_password
                        }
                    })

                    email_data = {
                        "email_body": html_content,
                        "email_subject": "Используйте новый пароль",
                        "to_email": user.email,
                    }

                    try:
                        Util.send_email(email_data)
                    except Exception as e:
                        return Response({"error": _("Ошибка при отправке почты: ") + str(e)}, status=500)

                    return Response(
                        {
                            "response": True,
                            "message": _("Новый пароль был отправлен на вашу электронную почту"),
                        }
                    )
                return Response(
                    {
                        "response": False,
                        "message": _("Пожалуйста, подтвердите ваш адрес электронной почты"),
                    },
                    status=400
                )
            except User.DoesNotExist:
                return Response(
                    {"message": _("Пользователь с таким адресом email не существует")},
                    status=404
                )
        return Response(serializer.errors, status=400)
    
    

class PasswordResetUpdateAPIView(views.APIView):
    serializer_class = PasswordResetUpdateSerializer

    def get(self, request, token):
        try:
            user = User.objects.get(password_reset_token=token)
            if user.password_reset_token == token:
                new_password = "".join(
                    choices(string.ascii_letters + string.digits, k=8)
                )
                user.set_password(new_password)
                user.password_reset_token = None
                user.save()

                email_body = f"Ваш новый пароль:\n\n" f"{new_password}"

                email_data = {
                    "email_body": email_body,
                    "email_subject": "Используйте новый пароль",
                    "to_email": user.email,
                }

                Util.send_email(email_data)

                return Response(
                    {
                        "response": True,
                        "message": _(
                            "Новый пароль был отправлен на вашу электронную почту"
                        ),
                    }
                )

        except ObjectDoesNotExist:
            return Response({"respons": False, "message": _("Неверный токен")})


class SetNewPasswordAPIView(views.APIView):
    serializer_class = SetNewPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            user = get_object_or_404(User, pk=request.user.pk)

            if not user.is_verified or not user.is_authenticated:
                return Response(
                    {"reponse": False, "message": "Вы неавторизованы"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            if not check_password(old_password, user.password):
                return Response(
                    {"response": False, "message": _("Старый пароль неверен!")}
                )

            # if not check_password(new_password, user.password):
            #     return Response(
            #         {
            #             "response": False,
            #             "message": _("Новый пароль не может быть похожим на старый"),
            #         }
            #     )

            user.set_password(new_password)
            user.save()
            return Response({"response": True, "message": _("Пароль успешно обновлен")})
        return Response(serializer.errors)


class GetUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.is_anonymous:
            if user.phone:
                data = get_user_by_phone(user.phone)

                return Response(data)
            return Response({"response": False})
        return Response({"response": False})


from rest_framework.exceptions import APIException
import json


class CatalogServiceAPIView(views.APIView):
    API_URL = 'https://api.u-on.ru/{key}/catalog-service/{page}.{_format}'

    def get(self, request, page, _format='json'):
        key = 'RxH3WeM378er81w4dMuF1649063416'  
        api_url = self.API_URL.format(key=key, page=page, _format=_format)

        try:
            response = requests.get(api_url)
            response.raise_for_status() 
            if _format == 'json':
                data = response.json()
            else:
                data = response.text
        except requests.RequestException as e:
            raise APIException(f"External API error: {e}")

        return Response(data, status=status.HTTP_200_OK)
