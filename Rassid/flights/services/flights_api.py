import requests
from django.conf import settings
from flights.models import Airport, Flight

API_URL = "http://api.aviationstack.com/v1/flights"
API_KEY = settings.AVIATIONSTACK_API_KEY


def safe_get(value, default=None):
    return value if value is not None else default


def fetch_flights():
    params = {
        "access_key": API_KEY,
        "limit": 10
    }

    print("USING KEY:", API_KEY)
    print("SENDING REQUEST TO:", API_URL)

    response = requests.get(API_URL, params=params)

    print("STATUS:", response.status_code)
    print("RAW RESPONSE:", response.text)

    if response.status_code != 200:
        return None

    return response.json()


def parse_flight_data(f):
    parsed = {
    "flightNumber": f_info.get("iata"),
    "airline": airline.get("name"),
    "status": flight.get("flight_status"),
    "origin": origin,
    "destination": destination,
    "departureTime": dep.get("scheduled"),
    "arrivalTime": arr.get("scheduled"),
}
    return parsed   




def get_airport_or_create(iata):
    if not iata:
        return None

    airport, _ = Airport.objects.get_or_create(
        code=iata,
        defaults={"name": iata}
    )
    return airport

def save_flights_to_db(flights_data):
    for flight in flights_data:
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})
        airline = flight.get("airline", {})
        f_info = flight.get("flight", {})

        origin, _ = Airport.objects.get_or_create(
            code=dep.get("iata"),
            defaults={
                "name": dep.get("airport") or dep.get("iata"),
                "city": dep.get("timezone") or "Unknown",
                "country": "Unknown",
            }
        )

        destination, _ = Airport.objects.get_or_create(
            code=arr.get("iata"),
            defaults={
                "name": arr.get("airport") or arr.get("iata"),
                "city": arr.get("timezone") or "Unknown",
                "country": "Unknown",
            }
        )

        parsed = {
            "status": flight.get("flight_status"),
            "scheduledDeparture": dep.get("scheduled"),
            "scheduledArrival": arr.get("scheduled"),
            "airlineCode": airline.get("iata"),
            "origin": origin,
            "destination": destination,
        }

        Flight.objects.update_or_create(
            flightNumber=f_info.get("iata"),
            defaults=parsed
        )
    
