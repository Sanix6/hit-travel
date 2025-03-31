from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers
from src.payment.models import Transaction
from .models import FlightRequest, Passengers, Segments


class SegmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Segments
        exclude = ["main"]


class PassengersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passengers
        exclude = ["main"]


class FlightsSerializer(serializers.ModelSerializer):
    segments = SegmentsSerializer(many=True)
    passengers = PassengersSerializer(many=True)
    book_class = serializers.SerializerMethodField()
    deeplink = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    timeout = serializers.SerializerMethodField()

    class Meta:
        model = FlightRequest
        fields = [
            "id",
            "status",
            "created_at",
            "billing_number",
            "amount",
            "book_class",
            "segments",
            "passengers",
            "deeplink",
            "timeout",
            "payler_url",
            "transaction_id",
        ]

    def get_book_class(self, obj):
        book = obj.book_class

        if book == "e":
            return f"Эконом класс"
        if book == "b":
            return f"Бизнес класс"
        if book == "f":
            return f"Первый класс"
        if book == "w":
            return f"Комфорт"
        return f"-"

    def get_deeplink(self, obj):
        request_type = self.context.get("request_type")
        if request_type == "detail":
            try:
                transaction = Transaction.objects.get(request_id=self.context.get("id"))
                return f"https://app.mbank.kg/deeplink?service=67ec3602-7c44-415c-a2cd-08d3376216f5&PARAM1={transaction.rid}&amount={obj.amount}"
            except Transaction.DoesNotExist:
                pass
        return None

    def get_status(self, obj):
        if obj.status:
            if obj.status == "booked":
                return f"Бронирован"
            if obj.status == "ticketed":
                return f"Оплачено"
            if obj.status == "canceled":
                return f"Отменено"

    def get_timeout(self, obj):
        expiration_time = obj.created_at + timedelta(minutes=25)
        current_time = timezone.now()

        time_left = expiration_time - current_time
        time_left_minutes = int(time_left.total_seconds() / 60)

        return max(time_left_minutes, 0)


class CancelBookingSerializer(serializers.Serializer):
    booking_id = serializers.UUIDField()
    billing_number = serializers.CharField()


class RefundAmountSerializer(serializers.Serializer):
    billing_number = serializers.CharField()
