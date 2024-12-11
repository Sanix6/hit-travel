import requests
from django.conf import settings

AUTHLOGIN='info@hit-travel.kg'
AUTHPASS='LuFXg44pbQzc'

def fetch_tour_data(hotelcode):
    url = f"http://tourvisor.ru/xml/hotel.php?authlogin={AUTHLOGIN}&authpass={AUTHPASS}&format=json&hotelcode={hotelcode}"
    response = requests.get(url)
    if response.status_code == 200:
        tour_data = response.json()
        print(tour_data)  
        return tour_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

fetch_tour_data("1395")  