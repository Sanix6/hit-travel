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
    response = requests.get(search_url)

    if response.status_code != 200:
        return None

    try:
        return response.json().get("result", {}).get("requestid")
    except KeyError:
        return None


def convert_currency(data, usd_exchange, eur_exchange):
    for hotel in data.get("data", {}).get("result", {}).get("hotel", []):
        if hotel["currency"] == "USD":
            hotel["currency"] = "KGS"
            hotel["price"] = int(hotel["price"] * usd_exchange)

            for tour in hotel.get("tours", {}).get("tour", []):
                if tour["currency"] == "USD":
                    tour["currency"] = "KGS"
                    tour["price"] = int(tour["price"] * usd_exchange)
                else:
                    tour["currency"] = "KGS"
                    tour["price"] = int(tour["price"] * eur_exchange)

        elif hotel["currency"] == "EUR":
            hotel["currency"] = "KGS"
            hotel["price"] = int(hotel["price"] * eur_exchange)

            for tour in hotel.get("tours", {}).get("tour", []):
                if tour["currency"] == "USD":
                    tour["currency"] = "KGS"
                    tour["price"] = int(tour["price"] * usd_exchange)
                else:
                    tour["currency"] = "KGS"
                    tour["price"] = int(tour["price"] * eur_exchange)

    return data


def fetch_result_data(authlogin, authpass, requestid, page):
    url = (
        f"http://tourvisor.ru/xml/result.php?format=json"
        f"&requestid={requestid}&authlogin={authlogin}"
        f"&authpass={authpass}&page={page}"
    )
    response = requests.get(url)

    if response.status_code != 200:
        return None

    return response.json()
