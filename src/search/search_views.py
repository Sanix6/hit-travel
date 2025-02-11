import time

import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from src.main.models import Currency

from .models import Countries
from .services import *
from .services import get_isfavorite, get_isrequested, get_requestedhotel
from .utils import convert_currency, fetch_result_data, get_search_result

authlogin = settings.AUTHLOGIN
authpass = settings.AUTHPASS

class SearchView(APIView):
    def get(self, request):

        query_params = request.query_params
        currency = query_params.get("currency")

        if currency == "99":
            usd_exchange = Currency.objects.get(currency="USD").purchase
            eur_exchange = Currency.objects.get(currency="EUR").purchase

            mutable_query_params = query_params.copy()
            pricefrom = int(query_params.get("pricefrom", 0))
            priceto = int(query_params.get("priceto", 0))
            page = query_params.get("page", 1)

            mutable_query_params["pricefrom"] = pricefrom / usd_exchange
            mutable_query_params["priceto"] = priceto / usd_exchange
            mutable_query_params["currency"] = "1"

            requestid = get_search_result(
                authlogin, authpass, mutable_query_params
            )
            if not requestid:
                return Response({"response": False}, status=400)

            time.sleep(6)

            data = fetch_result_data(self.authlogin, self.authpass, requestid, page)
            if not data:
                return Response({"response": False}, status=400)

            converted_data = convert_currency(data, usd_exchange, eur_exchange)
            return Response(converted_data)

        else:
            requestid = get_search_result(authlogin, authpass, query_params)
            if not requestid:
                return Response({"response": False}, status=400)

            page = query_params.get("page", 1)
            time.sleep(6)

            data = fetch_result_data(authlogin, authpass, requestid, page)
            if not data:
                return Response({"response": False}, status=400)

            return Response(data)

class FilterParams(APIView):
    def get(self, request):
        base_url = "http://tourvisor.ru/xml/list.php"
        options_url = (
            f"{base_url}?type=hotel,country,departure,meal,stars,operator"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )
        services_operators_url = (
            f"{base_url}?authlogin={authlogin}&authpass={authpass}"
            f"&format=json&type=services,operator"
        )

        options_data = fetch_tourvisor_data(options_url)
        services_operators_data = fetch_tourvisor_data(services_operators_url)

        if "error" in options_data or "error" in services_operators_data:
            return Response(
                {
                    "response": False,
                    "error": options_data.get("error")
                    or services_operators_data.get("error"),
                },
                status=500,
            )

        lists = options_data.get("lists", {})
        services_lists = services_operators_data.get("lists", {})

        lists["services"] = services_lists.get("services", [])
        lists["operators"] = services_lists.get("operators", [])

        options_data["lists"] = lists

        return Response(options_data, status=200)


class FilterHotels(APIView):
    def get(self, request):
        query_params = {
            "hotcountry": request.query_params.get("hotcountry"),
            "hotregion": request.query_params.get("hotregion"),
            "hotstars": request.query_params.get("hotstars"),
            "hotrating": request.query_params.get("hotrating"),
            "hotactive": request.query_params.get("hotactive"),
            "hotfamily": request.query_params.get("hotfamily"),
            "hothealth": request.query_params.get("hothealth"),
            "hotcity": request.query_params.get("hotcity"),
            "hotbeach": request.query_params.get("hotbeach"),
            "hotdeluxe": request.query_params.get("hotdeluxe"),
            "hotrelax": request.query_params.get("hotrelax"),
        }

        base_url = "http://tourvisor.ru/xml/list.php"
        url = build_url(
            base_url, authlogin, authpass, request.query_params, query_params
        )

        hotels_data = fetch_tourvisor_data(url)

        if "error" in hotels_data:
            return Response(
                {"response": False, "error": hotels_data["error"]}, status=500
            )

        return Response(hotels_data, status=200)


class FilterCountries(APIView):
    def get(self, request, departureid):
        url = f"http://tourvisor.ru/xml/list.php?type=country&cndep={departureid}&format=json&authpass={authpass}&authlogin={authlogin}"
        countries_data = fetch_tourvisor_data(url)

        if "error" in countries_data:
            return Response(
                {"response": False, "error": countries_data["error"]}, status=500
            )

        country_list = (
            countries_data.get("lists", {}).get("countries", {}).get("country", [])
        )

        country_list = [update_country_name(country) for country in country_list]
        db_countries = Countries.objects.all()
        country_list = add_country_images(country_list, db_countries)

        countries_data["lists"]["countries"]["country"] = country_list

        return Response(countries_data, status=200)


class RegCountryView(APIView):
    def get(self, request, regcountry):
        regions = requests.get(
            f"http://tourvisor.ru/xml/list.php?type=region,subregion&regcountry={regcountry}"
            f"&authlogin={authlogin}&authpass={authpass}"
        )

        if regions.status_code != 200:
            return Response({"response": False})
        return Response(regions.json())


class TourActualizeView(APIView):
    def get(self, request, tourid):
        actualize = requests.get(
            f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&request=0"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )

        if actualize.status_code != 200:
            return Response({"response": False})
        return Response(actualize.json()["data"])


class TourActdetailView(APIView):
    def get(self, request, tourid):
        actualize = requests.get(
            f"http://tourvisor.ru/xml/actdetail.php?tourid={tourid}"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )
        if actualize.status_code != 200:
            return Response({"response": False})
        return Response(actualize.json())


class HotelDetailView(APIView):
    def get(self, request, hotelcode):
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
        hottours = requests.get(
            f"http://tourvisor.ru/xml/hottours.php?city=80&city2=60&items=20&picturetype=1"
            f"&format=json&authpass={authpass}&authlogin={authlogin}&reviews=1"
        )

        if hottours.status_code != 200:
            return Response({"response": False})
        return Response(hottours.json())


class TourDetailView(APIView):

    def get(self, request, tourid):
        tour_url = f"http://tourvisor.ru/xml/actualize.php?tourid={tourid}&request=1&format=json&authpass={authpass}&authlogin={authlogin}"
        flights_url = f"http://tourvisor.ru/xml/actdetail.php?tourid={tourid}&format=json&authpass={authpass}&authlogin={authlogin}"
        user = request.user

        tour_data = fetch_tourvisor_data(tour_url)
        if (
            "error" in tour_data
            or "data" not in tour_data
            or "tour" not in tour_data["data"]
        ):
            return Response(
                {
                    "response": False,
                    "error": tour_data.get("error", "Tour data not available"),
                },
                status=500,
            )

        flights_data = fetch_tourvisor_data(flights_url)
        flights = flights_data.get("flights", {}) if "error" not in flights_data else {}

        response_data = {
            "isfavorite": get_isfavorite(user, tourid),
            "isrequested": get_isrequested(user, tourid),
            "tour": tour_data["data"]["tour"],
            "flights": flights,
        }

        return Response(response_data, status=200)


class RecommendationsView(APIView):
    def get(self, request):
        recommendations = requests.get(
            f"http://tourvisor.ru/xml/hottours.php?picturetype=1&items=30"
            f"&format=json&authpass={authpass}&authlogin={authlogin}"
        )

        if recommendations.status_code != 200:
            return Response({"response": False})
        return Response(recommendations.json())


class SearchToursByHotel(APIView):
    def get(self, request, hotels):
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
