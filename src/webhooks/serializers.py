from rest_framework import serializers

from .models import CreateClient, CreateRequest


class CreateRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateRequest
        fields = "__all__"


class CreateClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = CreateClient
        fields = "__all__"
