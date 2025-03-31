from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from urllib.parse import urlencode

import redis
import requests

from .models import AirProviders


def get_redis_token(redis_host="localhost", redis_port=6379, redis_db=1):
    try:
        redis_client = redis.StrictRedis(host=redis_host, port=6379, db=redis_db)
        return redis_client.get("token")
    except Exception as e:
        raise ConnectionError("Failed to connect to Redis or retrieve token") from e


def filter_flights(flights, is_refund_filter, is_baggage_filter):
    filtered_flights = []
    
    for flight in flights:
        if (is_refund_filter and not flight.get("is_refund")) or \
           (is_baggage_filter and not flight.get("is_baggage")):
            continue

        supplier = flight.get("provider", {}).get("supplier", {})
        title, code = supplier.get("title"), supplier.get("code")

        if not title or not code:
            continue  

        air_provider = AirProviders.objects.filter(code=code).only("img").first()

        supplier["logo"] = f"https://hit-travel.org/{air_provider.img.url}" if air_provider and air_provider.img else None
        filtered_flights.append(flight)

    return filtered_flights


def fetch_nearest_flights(offset, base_url, token, query_params, flight_date):
    try:
        nearest_date = (flight_date + timedelta(days=offset)).strftime("%d.%m.%Y")
        nearest_params = query_params.copy()
        nearest_params["segments[0][date]"] = nearest_date
        nearest_encoded_params = urlencode(nearest_params, safe="[]")
        nearest_url = f"{base_url}/avia/search-recommendations?auth_key={token}&{nearest_encoded_params}&count=1"
        nearest_response = requests.get(nearest_url.encode("utf-8"))
        nearest_data = nearest_response.json().get("data", {})
        nearest_flight = (
            nearest_data.get("flights", [])[0] if nearest_data.get("flights") else None
        )

        if nearest_flight:
            return {
                "date": nearest_date,
                "price": nearest_flight.get("price", {})
                .get("KGS", {})
                .get("amount", 0),
            }
    except Exception as e:
        return None


def format_nearest_flights(nearest_flights, original_date):
    days_of_week = ["пн", "вт", "ср", "чт", "пт", "сб", "вс"]
    formatted_flights = []
    for nearest_flight in nearest_flights:
        flight_date = datetime.strptime(nearest_flight["date"], "%d.%m.%Y")
        formatted_flights.append(
            {
                "date": f"{flight_date.day} {flight_date.strftime('%b')}, {days_of_week[flight_date.weekday()]}",
                "price": f"{nearest_flight['price']} сом",
                "active_day": (flight_date == original_date),
            }
        )
    return formatted_flights