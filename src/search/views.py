import requests
from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.utils import IntegrityError
from django.conf import settings
from .models import Favorites, Countries
from .serializers import *


class AddRemoveTourFavoriteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, tourid):
        user = request.user
        
        try:
            favorite, created = Favorites.objects.get_or_create(user=user, tourid=tourid)
            
            if not created:
                favorite.delete()
                return Response({
                    "response": True, 
                    "message": "Удалено из избранного"
                }, status=status.HTTP_200_OK)
            
            return Response({
                "response": True, 
                "message": "Добавлено в избранное"
            }, status=status.HTTP_201_CREATED)
        
        except IntegrityError as e:
            return Response({
                "response": False, 
                "message": "Ошибка базы данных", 
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        except Exception as e:
            return Response({
                "response": False, 
                "message": "Произошла ошибка", 
                "details": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class FavoriteToursListView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS
        
        queryset = Favorites.objects.filter(user=request.user)
        serializer = FavoriteToursSerializer(queryset, many=True)
        response = []
        
        for favorite in serializer.data:
            tourid = favorite.get('tourid')
            if not tourid:
                continue
            
            detail_url = f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&format=json&authpass={authpass}&authlogin={authlogin}"
            flights_url = f"http://tourvisor.ru/xml/actdetail.php?tourid={tourid}&format=json&authpass={authpass}&authlogin={authlogin}"
            
            d = {'tourid': tourid, 'isfavorite': True}
            
            try:
                detail_response = requests.get(detail_url)
                detail_response.raise_for_status()
                d['tour'] = detail_response.json().get('data', {}).get('tour', {})
            except (requests.exceptions.RequestException, KeyError) as e:
                d['tour'] = {}
                d['error'] = f"Error fetching tour details: {str(e)}"
            
            try: 
                flights_response = requests.get(flights_url)
                flights_response.raise_for_status()
                d['flights'] = flights_response.json().get('flights', {})
            except (requests.exceptions.RequestException, KeyError) as e:
                d['flights'] = {}
                d['error'] = f"Error fetching flight details: {str(e)}"
            
            response.append(d)
            
        return Response(response, status=status.HTTP_200_OK)


class FlightsParamView(views.APIView):
    def get(self, request):
        instances = Countries.objects.exclude(img='')
        data = CountrySerializer(instances, many=True, context={'request': request})
        return Response({"countries": data.data})