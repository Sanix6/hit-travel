import time
import requests
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .models import Countries
from rest_framework.permissions import IsAuthenticated
from src.main.models import Currency
from .services import get_isfavorite, get_isrequested, get_requestedhotel
from redis import Redis
import json

redis_client = Redis(host='localhost', port=6379, db=0)

class SearchView(APIView):
    authlogin = settings.AUTHLOGIN
    authpass = settings.AUTHPASS

    def get_search_result(self, query_params):
        search_url = (
            f"http://tourvisor.ru/xml/search.php?format=json"
            f"&authlogin={self.authlogin}&authpass={self.authpass}"
        )

        for param, value in query_params.items():
            if param == 'directOnly' and value == 'true':
                param = 'hideregular'
                value = 1
            search_url += f"&{param}={value}"

        requestid_response = requests.get(search_url)

        if requestid_response.status_code != 200:
            return Response({"response": False})

        try:
            return requestid_response.json().get("result", {}).get("requestid")
        except KeyError:
            return Response({"response": False})

    def save_hotel_data_to_redis(self, requestid, hotels):
        redis_key = f"search_result:{requestid}"
        redis_client.set(redis_key, json.dumps(hotels), ex=600) 

        for hotel in hotels:
            hotel_key = f"hotel:{hotel['hotelid']}"
            redis_client.set(hotel_key, json.dumps(hotel), ex=600)


    def get(self, request):
        query_params = request.query_params
        currency = query_params.get("currency")

        if currency == "99":
            mutable_query_params = query_params.copy()
            usd_exchange = Currency.objects.get(currency="USD").purchase
            eur_exchange = Currency.objects.get(currency="EUR").purchase

            pricefrom = int(query_params.get("pricefrom", 0))
            priceto = int(query_params.get("priceto", 0))
            page = query_params.get("page", 1)

            mutable_query_params["pricefrom"] = pricefrom / usd_exchange
            mutable_query_params["priceto"] = priceto / usd_exchange
            mutable_query_params["currency"] = "1"

            requestid = self.get_search_result(mutable_query_params)
            time.sleep(6)

            url = (
                f"http://tourvisor.ru/xml/result.php?format=json&requestid={requestid}"
                f"&authlogin={self.authlogin}&authpass={self.authpass}&page={page}"
            )

            response = requests.get(url)

            if response.status_code != 200:
                return Response({"response": False})

            data = response.json()
            hotels = data.get("data", {}).get("result", {}).get("hotel", [])
            
            # Обновление цен в KGS
            for hotel in hotels:
                if hotel["currency"] == "USD":
                    hotel["currency"] = "KGS"
                    hotel["price"] = int(hotel["price"] * usd_exchange)
                    for tour in hotel["tours"]["tour"]:
                        tour["currency"] = "KGS"
                        tour["price"] = int(tour["price"] * usd_exchange)
                elif hotel["currency"] == "EUR":
                    hotel["currency"] = "KGS"
                    hotel["price"] = int(hotel["price"] * eur_exchange)
                    for tour in hotel["tours"]["tour"]:
                        tour["currency"] = "KGS"
                        tour["price"] = int(tour["price"] * eur_exchange)

            self.save_hotel_data_to_redis(requestid, hotels)

            return Response(data)
        else:
            requestid = self.get_search_result(query_params)
            page = query_params.get("page", 1)

            time.sleep(6)

            url = (
                f"http://tourvisor.ru/xml/result.php?format=json&requestid={requestid}"
                f"&authlogin={self.authlogin}&authpass={self.authpass}&page={page}"
            )

            response = requests.get(url)

            if response.status_code != 200:
                return Response({"response": False})

            data = response.json()
            hotels = data.get("data", {}).get("result", {}).get("hotel", [])

            self.save_hotel_data_to_redis(requestid, hotels)

            return Response(data)
        


class FilterParams(APIView):
    def get(self, request):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        options = requests.get(
            f"http://tourvisor.ru/xml/list.php?type="
            f"hotel,country,departure,meal,stars,operator"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )
        options_data = options.json()

        services_operators = requests.get(
            f"http://tourvisor.ru/xml/list.php?authlogin={authlogin}&authpass={authpass}"
            f"&format=json&type=services,operator"
        ).json()["lists"]

        if options.status_code != 200:
            return Response({"response": False})

        options_data["lists"]["services"] = services_operators["services"]
        options_data["lists"]["operators"] = services_operators["operators"]

        return Response(options_data)


class FilterHotels(APIView):
    def get(self, request):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        hotcountry = request.query_params.get("hotcountry")
        hotregion = request.query_params.get("hotregion")
        hotstars = request.query_params.get("hotstars")
        hotrating = request.query_params.get("hotrating")
        hotactive = request.query_params.get("hotactive")
        hotrelax = request.query_params.get("hotrelax")
        hotfamily = request.query_params.get("hotfamily")
        hothealth = request.query_params.get("hothealth")
        hotcity = request.query_params.get("hotcity")
        hotbeach = request.query_params.get("hotbeach")
        hotdeluxe = request.query_params.get("hotdeluxe")

        url = "http://tourvisor.ru/xml/list.php?type=hotel&format=json"
        url += f"&authpass={authpass}&authlogin={authlogin}"

        if hotcountry:
            url += f"&hotcountry={hotcountry}"

        if hotregion:
            url += f"&hotregion={hotregion}"

        if hotstars:
            url += f"&hotstars={hotstars}"

        if hotactive:
            url += f"&hotactive={hotactive}"

        if hotrating:
            url += f"&hotrating={hotrating}"

        if hotfamily:
            url += f"&hotfamily={hotfamily}"

        if hothealth:
            url += f"&hothealth={hothealth}"

        if hotcity:
            url += f"&hotcity={hotcity}"

        if hotbeach:
            url += f"&hotbeach={hotbeach}"

        if hotdeluxe:
            url += f"&hotdeluxe={hotdeluxe}"

        if hotrelax:
            url += f"&hotrelax={hotrelax}"

        hotels = requests.get(url)

        if hotels.status_code != 200:
            return Response({"response": False})
        return Response(hotels.json())


class FilterCountries(APIView):
    def update_country_name(self, country):
        if country.get("name") == "Киргизия":
            country["name"] = "Кыргызстан"
        return country

    def get(self, request, departureid):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        countries = requests.get(
            f"http://tourvisor.ru/xml/list.php?type=country&cndep={departureid}"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )
        if countries.status_code != 200:
            return Response({"response": False})

        countries = countries.json()

        db = Countries.objects.all()
        for i1 in countries["lists"]["countries"]["country"]:
            for i2 in db:
                if i1['name'] == i2.name:
                    if i2.img:
                        i1["img"] = f'https://hit-travel.org{i2.img.url}'
                    else:
                        i1["img"] = None

            if i1["name"] == "Киргизия":
                i1["name"] = "Кыргызстан"

        return Response(countries)


class RegCountryView(APIView):
    def get(self, request, regcountry):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        regions = requests.get(
            f"http://tourvisor.ru/xml/list.php?type=region,subregion&regcountry={regcountry}"
            f"&authlogin={authlogin}&authpass={authpass}"
        )

        if regions.status_code != 200:
            return Response({"response": False})
        return Response(regions.json())


class TourActualizeView(APIView):
    def get(self, request, tourid):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        actualize = requests.get(
            f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&request=0"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )

        if actualize.status_code != 200:
            return Response({"response": False})
        return Response(actualize.json()["data"])


class TourActdetailView(APIView):
    def get(self, request, tourid):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        actualize = requests.get(
            f"http://tourvisor.ru/xml/actdetail.php?tourid={tourid}"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )
        if actualize.status_code != 200:
            return Response({"response": False})
        return Response(actualize.json())


class HotelDetailView(APIView):
    def get(self, request, hotelcode):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS        

        hoteldetail_response = requests.get(
            f"http://tourvisor.ru/xml/hotel.php?hotelcode={hotelcode}"
            f"&format=json&authpass={authpass}&authlogin={authlogin}&reviews=1"
        )
        if hoteldetail_response.status_code != 200:
            return Response({"response": False})
        
        hoteldetail_json = hoteldetail_response.json()
        hoteldetail_json["data"]["key"] = get_requestedhotel(request.user, hotelcode)
        return Response(hoteldetail_json["data"])



class HotToursListView(APIView):
    def get(self, request):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        hottours = requests.get(
            f"http://tourvisor.ru/xml/hottours.php?city=80&city2=60&items=20&picturetype=1"
            f"&format=json&authpass={authpass}&authlogin={authlogin}&reviews=1"
        )

        if hottours.status_code != 200:
            return Response({"response": False})
        return Response(hottours.json())


class TourDetailView(APIView):
    # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, tourid):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS
        user = request.user

        # Get hotelcode to return hotel detail
        try:
            tour = requests.get(
                f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&request=1"
                f"&format=json&authpass={authpass}&authlogin={authlogin}"
            )

            if tour.status_code != 200:
                return Response({"response": False})
        except KeyError:
            return Response({"response": False})

        # try:
        #     hoteldetail = requests.get(
        #         f"http://tourvisor.ru/xml/hotel.php?hotelcode={tour.json()['data']['tour']['hotelcode']}"
        #         f"&format=json&authpass={authpass}&authlogin={authlogin}&reviews=1"
        #     )

        #     if hoteldetail.status_code != 200:
        #         return Response({"response": False})
        # except KeyError:
        #     return Response({"reponse": False})

        # Get flights on this tour
        try:
            flights = requests.get(
                f"http://tourvisor.ru/xml/actdetail.php?tourid={tourid}"
                f"&format=json&authpass={authpass}&authlogin={authlogin}"
            )
            if flights.status_code != 200:
                return Response({"response": False})
            flights = flights.json()["flights"]
        except KeyError:
            flights = flights.json()

        return Response(
            {
                "isfavorite": get_isfavorite(user, tourid),
                "isrequested": get_isrequested(user, tourid),
                # "hotel": hoteldetail.json()["data"]["hotel"],
                "tour": tour.json()["data"]["tour"],
                "flights": flights,
            }
        )


class RecommendationsView(APIView):
    def get(self, request):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS

        recommendations = requests.get(
            f"http://tourvisor.ru/xml/hottours.php?picturetype=1&items=30"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )

        if recommendations.status_code != 200:
            return Response({"response": False})
        return Response(recommendations.json())


class SearchToursByHotel(APIView):
    def get(self, request, hotels):
        authlogin = settings.AUTHLOGIN
        authpass = settings.AUTHPASS
        
        search_result = requests.get(
            f"http://tourvisor.ru/xml/search.php?format=json&hotels={hotels}"
            f"&authlogin={authlogin}&authpass={authpass}"
        )
        
        requestid = search_result.json()["result"]["requestid"]
        
        time.sleep(2)
        
        result = requests.get(
            f"http://tourvisor.ru/xml/result.php?format=json&requestid={requestid}"
            f"&authlogin={authlogin}&authpass={authpass}"
        )
        
        return Response(result.json())
    

