from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.Serializer):
    order_id = serializers.UUIDField(required=True)

    class Meta:
        fields = ('order_id',)
        