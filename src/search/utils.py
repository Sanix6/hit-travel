import requests
from rest_framework.response import Response
import time

def build_search_url(authlogin, authpass, query_params):
    base_url = (
        f"http://tourvisor.ru/xml/search.php?format=json"
        f"&authlogin={authlogin}&authpass={authpass}"
    )
    params = "&".join(f"{key}={value}" for key, value in query_params.items() if key != "directOnly")
    return f"{base_url}&{params}"

def get_search_result(authlogin, authpass, query_params):
    search_url = build_search_url(authlogin, authpass, query_params)
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        return response.json().get("result", {}).get("requestid")
    except (requests.exceptions.RequestException, KeyError) as e:
        return {"error": f"Failed to get search result: {str(e)}"}


def convert_currency(data, usd_exchange, eur_exchange):
    for hotel in data.get("data", {}).get("result", {}).get("hotel", []):
        hotel_currency = hotel.get("currency")
        if hotel_currency in ("USD", "EUR"):
            exchange_rate = usd_exchange if hotel_currency == "USD" else eur_exchange
            hotel["currency"] = "KGS"
            hotel["price"] = int(hotel.get("price", 0) * exchange_rate)
            
            for tour in hotel.get("tours", {}).get("tour", []):
                tour_currency = tour.get("currency")
                exchange_rate = usd_exchange if tour_currency == "USD" else eur_exchange
                tour["currency"] = "KGS"
                tour["price"] = int(tour.get("price", 0) * exchange_rate)
    
    return data

def fetch_result_data(authlogin, authpass, requestid, page):
    url = (
        f"http://tourvisor.ru/xml/result.php?format=json"
        f"&requestid={requestid}&authlogin={authlogin}"
        f"&authpass={authpass}&page={page}"
    )
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": f"Failed to fetch result data: {str(e)}"}
