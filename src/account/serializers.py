import locale
import requests
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import json
from src.account.models import *
from src.payment.models import Transaction

locale.setlocale(locale.LC_TIME, "ru_RU.UTF-8")


class PaymentsSerializer(serializers.ModelSerializer):
    img = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()

    class Meta:
        model = Payments
        fields = ["img", "description", "bank_name", "icon"]

    def get_img(self, obj):
        if obj.img:
            return f"https://hit-travel.org/media/{obj.img}"
        return None

    def get_icon(self, obj):
        if obj.icon:
            return f"https://hit-travel.org/media/{obj.icon}"
        return None


class RegisterAPIViewSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        required=True,
        min_length=4,
        error_messages={"min_length": "Не менее 4 символов."},
    )

    class Meta:
        model = User
        fields = [
            "email",
            "phone",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
        ]


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.IntegerField()

    class Meta:
        fields = ["email", "code"]


class SendAgainCodeSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        write_only=True,
        required=True,
    )
    password = serializers.CharField(
        write_only=True,
        min_length=4,
        required=True,
        error_messages={"min_length": "Не менее 4 символов."},
    )
    token = serializers.CharField(read_only=True)
    # email = serializers.EmailField(
    #     label=_("Email"), style={"input_type": "email"}, write_only=True
    # )
    # password = serializers.CharField(
    #     label=_("Password"),
    #     style={"input_type": "password"},
    #     trim_whitespace=False,
    #     write_only=True,
    #     required=True,
    #     min_length=8,
    #     error_messages={
    #         'min_length': 'Не менее 8 символов.'
    #     }
    # )
    # token = serializers.CharField(label=_("Token"), read_only=True)

    # def validate(self, attrs):
    #     email = attrs.get("email")
    #     password = attrs.get("password")

    #     if email and password:
    #         user = authenticate(
    #             request=self.context.get("request"), username=email, password=password
    #         )

    #         if not user:
    #             return Response(
    #                 {
    #                     "response": False,
    #                     "message": "Невозможно войти в систему с указанными учетными данными",
    #                 }
    #             )
    #     else:
    #         msg = _("Должен включать имя пользователя и пароль")
    #         raise serializers.ValidationError(msg, code="authorization")

    #     attrs["user"] = user
    #     return attrs


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    class Meta:
        fields = ["email"]


class PasswordResetUpdateSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ["password", "confirm_password"]

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs


class SetNewPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        fields = ["old_password", "new_password", "confirm_password"]

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        confirm_password = attrs.get("confirm_password")

        if new_password != confirm_password:
            raise serializers.ValidationError({"error": "Пароли не совпадают"})
        return attrs


class UpdateProfilePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["photo"]


class BonusHistorySerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    valid = serializers.SerializerMethodField()

    class Meta:
        model = BonusHistory
        fields = ["id", "name", "sum", "currency", "created_at", "valid"]

    def get_created_at(self, obj):
        return obj.created_at.strftime("%d %B %Y %H:%M")

    def get_valid(self, obj):
        return obj.valid.strftime("%d %B %Y")


class PersonalInfoSerializer(serializers.ModelSerializer):
    photo = serializers.SerializerMethodField()
    date_joined = serializers.SerializerMethodField()
    last_login = serializers.SerializerMethodField()
    # bonus_history = BonusHistorySerializer(many=True)
    bonuses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "date_joined",
            "last_login",
            "photo",
            "bonuses",
            "inn",
            "passport_id",
            "date_of_issue",
            "issued_by",
            "validity",
            "dateofborn",
            "city",
            "county"
            # "bonus_history",
        ]

    def get_bonuses(self, obj):
        if obj.tourist_id:
            bonuses = requests.get(
                f"https://api.u-on.ru/{settings.KEY}/user/{obj.tourist_id}.json"
            )

            if bonuses.status_code != 200:
                return None
            
            bcard_value = bonuses.json().get("user", [])[0].get("bcard_value", None)
            return bcard_value

             
        return None

    def get_photo(self, obj):
        if obj.photo:
            request = self.context.get("request")
            photo_url = obj.photo.url
            return f"https://hit-travel.org/{photo_url}"
        return None

    def get_date_joined(self, obj):
        return obj.date_joined.strftime("%Y/%m/%d %H:%M")

    def get_last_login(self, obj):
        if obj.last_login:
            return obj.last_login.strftime("%Y/%m/%d %H:%M")


class MyTourSerializer(serializers.ModelSerializer):
    class Meta:
        model = RequestTour
        fields = "__all__"


class UpdateInfoSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ["first_name", "last_name"]


class TravelerSerializer(serializers.ModelSerializer):
    dateofborn = serializers.DateField(required=False)
    class Meta:
        model = Traveler
        fields = ['first_name', 'last_name', 'dateofborn', 'passport_id', 'issued_by']



class DocumentsSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["id", "name", "file"]

    def get_file(self, obj):
        if obj.file:
            return f"https://hit-travel.org{obj.file.url}"
        return None


class TourRequestSerializer(serializers.ModelSerializer):
    travelers = TravelerSerializer(many=True, required=False)
    documents = DocumentsSerializer(many=True, required=False, read_only=True)
    passport_front = serializers.FileField(allow_empty_file=True, required=False)
    passport_back = serializers.FileField(allow_empty_file=True, required=False)
    payler_url = serializers.SerializerMethodField(read_only=True)
    transaction_id = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = RequestTour
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone",
            "email",
            "gender",
            "dateofborn",
            "inn",
            "tourid",
            "operatorlink",
            "travelers",
            "city",
            "country",
            "passport_id",
            "bonuses",
            "price",
            "paid",
            "currency",
            "passport_front",
            "passport_back",
            "date_of_issue",
            "issued_by",
            "validity",
            "documents",
            "agreement",
            "manager",
            "payler_url",
            "transaction_id",
        ]

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    dateofborn = serializers.DateField(required=True)
    passport_id = serializers.CharField(required=True)
    gender = serializers.CharField(required=True)
    city = serializers.CharField(required=True)
    country = serializers.CharField(required=True)
    date_of_issue = serializers.DateField(required=True)
    issued_by = serializers.CharField(required=True)
    validity = serializers.DateField(required=True)
    inn = serializers.CharField(required=True)

    def get_payler_url(self, obj): 
        return obj.payler_url

    def get_transaction_id(self, obj): 
        return obj.transaction_id

    def create(self, validated_data):
        try:
            travelers_list = validated_data.pop("travelers", [])
            with open('example.txt', 'a') as file:
                file.write(f"{validated_data},\n\n\n")
            instance = RequestTour.objects.create(**validated_data)
            for traveler in travelers_list:
                instance.travelers.create(**traveler)
            return instance
        except KeyError:
            return super().create(validated_data)

# if data from U-on
# class TouristSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tourist
#         fields = ['tourist_id']


# class AddDocumentsViewSerializer(serializers.Serializer):
#     passport_front = serializers.FileField(allow_empty_file=False)
#     passport_back = serializers.FileField(allow_empty_file=False)


class FAQListSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = "__all__"


class TourHistorySerializers():
    pass

from src.payment.models import Transaction


class HotelTravelerSerializer(serializers.ModelSerializer):
    dateofborn = serializers.DateField(required=False)
    class Meta:
        model = HotelTraveler
        fields = ['first_name', 'last_name', 'dateofborn', 'passport_id', 'issued_by']


class RequestHotelSerializer(serializers.ModelSerializer):
    deeplink = serializers.SerializerMethodField(read_only=True)
    amount = serializers.SerializerMethodField(read_only=True)
    payler_url = serializers.SerializerMethodField(read_only=True)
    travelers = HotelTravelerSerializer(many=True, required=False)
    
    class Meta:
        model = RequestHotel
        fields = [
            'id', 'hotelid', 'first_name', 'phone', 'email', 'price', 'paid', 
            'amount', 'currency', 'deeplink', 'payler_url', 'travelers', 
            'nights', 'flydate', 'placement', 'adults', 'child', 'mealcode', 
            'mealrussian', 'meal'
        ]

    def get_deeplink(self, obj):
        if self.context.get("type") == "detail": 
            try:
                transaction = Transaction.objects.get(hotel_id=self.context.get('id'))
                return f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={transaction.amount}"
            except Transaction.DoesNotExist:
                pass
        return None

    def get_amount(self, obj): 
        return obj.price
    
    def get_payler_url(self, obj): 
        return obj.payler_url

    def create(self, validated_data):
        try:
            travelers_list = validated_data.pop("travelers", [])
            with open('hotel_travelers.txt', 'a') as file:
                file.write(f"{validated_data},\n\n\n")
            instance = RequestHotel.objects.create(**validated_data)
            for traveler in travelers_list:
                instance.travelers.create(**traveler)
            
            return instance
        except KeyError:
            return super().create(validated_data)



    

class ManualRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ManualRequests
        fields = "__all__"

    
    def to_representation(self, instance):
        url = f"https://api.u-on.ru/{settings.KEY}/request/{instance.request_id}.json"
        response = requests.get(url)
        
        if response.status_code != 200:
            return {}

        data = response.json().get("request", [])

        if not data or (isinstance(data, list) and len(data) == 0):
            return {}
        
        instance.data = data[0]
        return super().to_representation(instance)
    

class ExtendedFieldSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=True)
    section = serializers.IntegerField(required=True)
    name = serializers.CharField(max_length=255, required=True)
    type = serializers.IntegerField(required=False, default=1)
    options = serializers.ListField(
        child=serializers.CharField(max_length=255), 
        required=False, 
        allow_empty=True
    )