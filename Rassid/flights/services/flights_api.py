import requests
from django.conf import settings
from flights.models import Airport, Flight

API_URL = "https://api.aviationstack.com/v1/flights"
API_KEY = settings.AVIATIONSTACK_API_KEY


def safe_get(value, default=None):
    return value if value is not None else default


def fetch_flights(airport_code=None):
    params = {
        "access_key": API_KEY,
        "limit": 100
    }
    if airport_code:
        params["dep_iata"] = airport_code

    print("USING KEY:", API_KEY)
    print("SENDING REQUEST TO:", API_URL)

    try:
        response = requests.get(API_URL, params=params)
        print("STATUS:", response.status_code)
        print("RAW RESPONSE:", response.text)

        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")

        return response.json()
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network Error: {str(e)}")

    return response.json()







def get_airport_or_create(iata):
    if not iata:
        return None

    airport, _ = Airport.objects.get_or_create(
        code=iata,
        defaults={"name": iata}
    )
    return airport

def save_flights_to_db(flights_data):
    if isinstance(flights_data, dict):
        flights_list = flights_data.get('data', [])
    elif isinstance(flights_data, list):
        flights_list = flights_data
    else:
        flights_list = []
        
    print(f"DEBUG: Processing {len(flights_list)} flights...")

    for index, flight in enumerate(flights_list):
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})
        airline = flight.get("airline", {})
        f_info = flight.get("flight", {})
        
        # Skip flights without an IATA code (flightNumber is required)
        flight_number = f_info.get("iata")
        if not flight_number:
            continue

        # Helper to get better city name
        def get_city_or_name(data):
            # Prefer explicit city if available (rare in this API subset without paid)
            # Fallback to Airport Name. Timezone is too broad (e.g. Asia/Riyadh covers DMM, JED)
            return data.get("airport") or data.get("iata") or "Unknown"

        origin, _ = Airport.objects.update_or_create(
            code=dep.get("iata"),
            defaults={
                "name": dep.get("airport") or dep.get("iata"),
                "city": get_city_or_name(dep),
                "country": dep.get("country") or "Unknown",
            }
        )

        origin, _ = Airport.objects.update_or_create(
            code=dep.get("iata"),
            defaults={
                "name": dep.get("airport") or dep.get("iata"),
                "city": get_city_or_name(dep),
                "country": dep.get("country") or "Unknown",
            }
        )

        destination, _ = Airport.objects.update_or_create(
            code=arr.get("iata"),
            defaults={
                "name": arr.get("airport") or arr.get("iata"),
                "city": get_city_or_name(arr),
                "country": arr.get("country") or "Unknown",
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

        # Try to get existing flight
        flight_obj = Flight.objects.filter(flightNumber=f_info.get("iata")).first()
        
        if flight_obj:
            if not flight_obj.is_protected:
                # Protect local automation (Boarding/Final Call) from being overwritten by "scheduled"/"active" from API
                current_local = flight_obj.status.lower()
                incoming_api = parsed.get("status", "").lower()
                
                if current_local in ['boarding', 'final call'] and incoming_api in ['scheduled', 'active']:
                    # Keep the local status, ignore the API status for this specific field
                    del parsed['status']

                # Update allowed
                for key, value in parsed.items():
                    setattr(flight_obj, key, value)
                flight_obj.save()
            else:
                # Protected: Do not update fields, but we might want to log it or do nothing.
                # However, let's keep Gate logic separate if we had it here, but we don't.
                pass
        else:
            # Create new
            Flight.objects.create(
                flightNumber=f_info.get("iata"),
                # Unpack parsed
                **parsed
            )
    
