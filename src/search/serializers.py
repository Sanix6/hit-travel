from rest_framework import serializers
from .models import *


class FavoriteToursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorites
        fields = '__all__'



class AirportsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airports
        fields = ['id', 'name', 'code_name']


class CitiesSerializer(serializers.ModelSerializer):
    airports = AirportsSerializer(many=True, read_only=True)

    class Meta:
        model = Cities
        fields = ['id', 'name', 'code_name', 'airports']


class CountrySerializer(serializers.ModelSerializer):
    cities = CitiesSerializer(many=True, read_only=True)
    img = serializers.SerializerMethodField()

    class Meta:
        model =Countries
        fields = ['id', 'name', 'code_name', 'img', 'cities']

    def get_img(self, obj):
        if obj.img:
            return f"https://hit-travel.org{obj.img.url}"
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from_city_code = self.context['request'].query_params.get('from')

        if from_city_code:
            filtered_cities = representation['cities'][:]
            filtered_cities = [city for city in filtered_cities if city['code_name'].upper() != from_city_code.upper()]
            representation['cities'] = filtered_cities

        return representation