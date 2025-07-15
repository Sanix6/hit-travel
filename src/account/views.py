import string
from datetime import datetime, timedelta, timezone
from random import choices, randint
import os

from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, permissions, status, views
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from ..base.utils import Util, send_sms
from .functions import *
from .serializers import *
from .services import *
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PaymentsAPIView(views.APIView):
    def get(self, request):
        payments = Payments.objects.all()
        serializer = PaymentsSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class RegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterAPIViewSerializer

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

        if serializer.is_valid():
            email = serializer.validated_data["email"]
            first_name = serializer.validated_data["first_name"]
            last_name = serializer.validated_data["last_name"]
            password = serializer.validated_data["password"]
            confirm_password = serializer.validated_data["confirm_password"]
            phone = serializer.validated_data["phone"]

            if password != confirm_password:
                return Response({"response": False, "password": "Пароли не совпадают."})
            
            user = User(
                email=email, first_name=first_name, last_name=last_name, phone=phone
            )
            user.set_password(password)
            user.save()

            user.is_verified = False
            user.verification_code_time = datetime.now()
            user.verification_code = randint(100_000, 999_999)
            user.save()

            sms_message = "Ваш код подтверждения регистрации: "
            send_sms(phone, sms_message, user.verification_code)

            add_bonuses = decrease_bonuses(user.bcard_id, 1000, "Бонус за регистрацию")

            return Response({"response": True}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors)



# class VerifyEmailAPIView(views.APIView):
#     serializer_class = VerifyPhoneSerializer

#     @swagger_auto_schema(
#         request_body=VerifyPhoneSerializer,
#         responses={
#             200: openapi.Response(description="Успешная верификация"),
#             400: openapi.Response(description="Ошибки валидации"),
#             404: openapi.Response(description="Пользователь не найден"),
#         },
#         operation_summary="Подтверждение телефона",
#         operation_description="Подтверждение телефона по коду из SMS",
#         tags=["Аутентификация"]
#     )
#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
        

#         if not serializer.is_valid():
#             phone_log_file = 'verify-phone.log'
#             with open(phone_log_file, 'w', encoding='utf-8') as phone_log:
#                 phone_log.write(serializer, '\n')
#             return Response(
#                 {"response": False, "detail": serializer.errors},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )

#         phone = serializer.validated_data["phone"]
#         code = serializer.validated_data["code"]

#         try:
#             user = User.objects.get(phone=phone)
#         except ObjectDoesNotExist:
#             return Response(
#                 {
#                     "response": False,
#                     "message": "Пользователь с таким телефоном не существует",
#                 },
#                 status=status.HTTP_404_NOT_FOUND,
#             )

#         if user.is_verified:
#             return Response({"message": "Аккаунт уже подтвержден"})

#         if not self.is_verification_code_valid(user, code):
#             return Response(
#                 {"response": False, "message": "Срок действия кода истек или код неверный!"}
#             )

#         user.is_verified = True
#         user.save()

#         token, _ = Token.objects.get_or_create(user=user)
#         return Response(
#             {
#                 "response": True,
#                 "message": "Верификация прошла успешно!",
#                 "token": token.key,
#                 "phone": user.phone,
#             }
#         )

#     def is_verification_code_valid(self, user, code):
#         if user.verification_code_time:
#             expiration_time = user.verification_code_time + timedelta(minutes=30)
#             expiration_time = expiration_time.replace(tzinfo=timezone.utc)

#             if (
#                 datetime.now(timezone.utc) < expiration_time
#                 and user.verification_code == code
#             ):
#                 return True

#         user.verification_code = None
#         user.verification_code_time = None
#         user.save()
#         return False
    

class VerifyPhoneView(generics.GenericAPIView):
    serializer_class = VerifyPhoneSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            code = serializer.data["code"]
            phone = serializer.data["phone"]

            with open('phones_log.txt', 'w', encoding='utf-8') as file:
                file.write(f"📞 Номер {phone} код-подтвр: {code}", )

            try:
                user = User.objects.get(phone=phone)

                if user.is_verified:
                    return Response({"message": _("Аккаунт уже подтвержден")})

                if user.verification_code == code:
                    user.is_verified = True
                    user.save()

                    token, created = Token.objects.get_or_create(user=user)

                    return Response(
                        {
                            "response": True,
                            "message": _("Пользователь успешно зарегистрирован."),
                            "token": token.key,
                        }
                    )
                return Response(
                    {"response": False, "message": _("Введен неверный код")}
                )
            except ObjectDoesNotExist:
                return Response(
                    {
                        "response": False,
                        "message": _("Пользователь с таким телефоном не существует"),
                    }
                )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

class SendAgainCodeAPIView(generics.GenericAPIView):
    serializer_class = SendAgainCodeSerializer 

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"response": False, "detail": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        phone = serializer.validated_data["phone"]

        try:
            user = User.objects.get(phone=phone)
        except ObjectDoesNotExist:
            return Response(
                {
                    "response": False,
                    "message": "Пользователь с таким телефоном не существует",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        if user.is_verified:
            return Response(
                {"response": False, "message": "Аккаунт уже подтвержден"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.verification_code = randint(100_000, 999_999)
        user.verification_code_time = datetime.now()
        user.save()

        sms_message = "Ваш новый код подтверждения: "
        send_sms(user.phone, sms_message, user.verification_code)

        return Response(
            {"response": True, "message": "Код подтверждения отправлен по SMS"}
        )


class LoginAPIView(views.APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = request.data.get("email")
        password = request.data.get("password")

        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return Response(
                {
                    "response": False,
                    "message": "Пользователь с указанными учетными данными не существует",
                },
            )

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                {
                    "response": False,
                    "message": "Невозможно войти в систему с указанными учетными данными",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_verified:
            return Response(
                {
                    "response": False,
                    "message": "Потвердите адрес электронной почты",
                    "isactivated": False,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {
                "response": True,
                "isactivated": True,
                "token": token.key,
                "email": user.email,
            },
            status=status.HTTP_200_OK,
        )


class LogoutAPIView(views.APIView):
    def get(self, request):
        user = request.user
        if user.is_authenticated:
            try:
                token = Token.objects.get(user=user)
                token.delete()
                return Response({"response": True, "message": "Выход выполнен успешно"})
            except ObjectDoesNotExist:
                return Response(
                    {"reponse": False, "message": "Пользователь не авторизован"}
                )
        return Response({"response": False, "message": "Пользователь не авторизован"})


class PasswordResetRequestAPIView(views.APIView):
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "Пользователь с таким адресом email не существует"},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not user.is_verified:
            return Response(
                {
                    "response": False,
                    "message": "Пожалуйста, подтвердите ваш адрес электронной почты",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_password = "".join(choices(string.ascii_letters + string.digits, k=8))
        user.set_password(new_password)
        user.password_reset_token = None
        user.save()

        html_content = render_to_string(
            "password_reset_email.html",
            {
                "data": {
                    "name": user.first_name,
                    "email": user.email,
                    "new_password": new_password,
                }
            },
        )

        email_data = {
            "email_body": html_content,
            "email_subject": "Используйте новый пароль",
            "to_email": user.email,
        }
        try:
            Util.send_email(email_data)
        except Exception as e:
            return Response(
                {"error": "Ошибка при отправке почты: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "response": True,
                "message": "Новый пароль был отправлен на вашу электронную почту",
            },
            status=status.HTTP_200_OK,
        )


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
                        "message": "Новый пароль был отправлен на вашу электронную почту",
                    }
                )
        except ObjectDoesNotExist:
            return Response({"respons": False, "message": "Неверный токен"})


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
                    {"response": False, "message": "Старый пароль неверен!"}
                )
            user.set_password(new_password)
            user.save()
            return Response({"response": True, "message": "Пароль успешно обновлен"})
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
