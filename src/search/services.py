import requests

from src.account.models import RequestHotel, RequestTour

from .models import Favorites


def fetch_tourvisor_data(url):
    """Helper function to fetch data from the Tourvisor API and return JSON response."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to fetch data: {str(e)}"}


def update_country_name(country):
    if country.get("name") == "Киргизия":
        country["name"] = "Кыргызстан"
    return country


def add_country_images(countries, db_countries):
    for api_country in countries:
        for db_country in db_countries:
            if api_country["name"] == db_country.name:
                api_country["img"] = (
                    f"https://hit-travel.org{db_country.img.url}"
                    if db_country.img
                    else None
                )
    return countries


def fetch_tourvisor_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to fetch data: {str(e)}"}


def build_url(base_url, authlogin, authpass, query_params, filters):
    """Helper function to construct the URL with filters for the Tourvisor API."""
    url = f"{base_url}?type=hotel&format=json&authpass={authpass}&authlogin={authlogin}"

    for param, value in filters.items():
        if value:
            url += f"&{param}={value}"

    return url


def fetch_tourvisor_data(url):
    """Helper function to fetch data from the Tourvisor API and return JSON response."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Failed to fetch data: {str(e)}"}


def check_user_request_exists(model, user, lookup_field, lookup_value):
    if user.is_anonymous:
        return False

    filter_kwargs = {"user": user, lookup_field: int(lookup_value)}
    return model.objects.filter(**filter_kwargs).exists()


def get_isfavorite(user, tourid):
    return check_user_request_exists(Favorites, user, "tourid", tourid)


def get_isrequested(user, tourid):
    return check_user_request_exists(RequestTour, user, "tourid", tourid)


def get_requestedhotel(user, hotelcode):
    return check_user_request_exists(RequestHotel, user, "hotelid", hotelcode)
