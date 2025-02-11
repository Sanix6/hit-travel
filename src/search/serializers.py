from urllib.parse import urljoin

from rest_framework import serializers

from .models import Airports, Cities, Countries, Favorites


class FavoriteToursSerializer(serializers.ModelSerializer):
    """Serializer for user's favorite tours."""

    class Meta:
        model = Favorites
        fields = "__all__"


class AirportsSerializer(serializers.ModelSerializer):
    """Serializer for airport information."""

    class Meta:
        model = Airports
        fields = ["id", "name", "code_name"]


class CitiesSerializer(serializers.ModelSerializer):
    airports = AirportsSerializer(many=True, read_only=True)

    class Meta:
        model = Cities
        fields = ["id", "name", "code_name", "airports"]


class CountrySerializer(serializers.ModelSerializer):
    cities = CitiesSerializer(many=True, read_only=True)
    img = serializers.SerializerMethodField()

    class Meta:
        model = Countries
        fields = ["id", "name", "code_name", "img", "cities"]

    def get_img(self, obj):
        if obj.img:
            return urljoin("https://hit-travel.org", obj.img.url)
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get("request")
        if request is None:
            return representation

        from_city_code = request.query_params.get("from")
        if from_city_code:
            from_city_code_upper = from_city_code.upper()
            representation["cities"] = [
                city
                for city in representation.get("cities", [])
                if city.get("code_name", "").upper() != from_city_code_upper
            ]

        return representation
