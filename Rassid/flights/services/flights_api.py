import requests
from django.conf import settings
from flights.models import Airport, Flight

API_URL = "http://api.aviationstack.com/v1/flights"
API_KEY = settings.AVIATIONSTACK_API_KEY.strip() if settings.AVIATIONSTACK_API_KEY else None


def safe_get(value, default=None):
    return value if value is not None else default


def fetch_flights():
    all_flights = []
    
    priority_airports = ['RUH', 'JED', 'DMM', 'DXB'] 
    
    print("Starting Priority Fetch...")
    for airport_code in priority_airports:
        print(f"Fetching departures for {airport_code}...")
        try:
            params = {
                "access_key": API_KEY,
                "limit": 50,
                "dep_iata": airport_code
            }
            response = requests.get(API_URL, params=params)
            if response.status_code == 200:
                data = response.json().get('data', [])
                print(f"  > Got {len(data)} flights for {airport_code}")
                all_flights.extend(data)
            else:
                print(f"  > Failed {airport_code}: {response.status_code}")
        except Exception as e:
            print(f"  > Error {airport_code}: {e}")

    print(f"Total flights fetched: {len(all_flights)}")
    return {'data': all_flights}


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

def fetch_airports(limit=100, search=None):
    if not API_KEY:
        print("No API Key found.")
        return []
        
    url = "http://api.aviationstack.com/v1/airports"
    params = {
        'access_key': API_KEY,
        'limit': limit
    }
    if search:
        params['search'] = search
        
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            return data.get('data', [])
        else:
            print(f"Failed to fetch airports: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error fetching airports: {e}")
        return []

def save_airports_to_db(airports_data):
    count = 0
    for item in airports_data:
        try:
            name = item.get('airport_name')
            iata_code = item.get('iata_code')
            city = item.get('city_iata_code')
            country = item.get('country_name')
            
            if not iata_code: 
                continue
                
            Airport.objects.update_or_create(
                code=iata_code,
                defaults={
                    'name': name,
                    'city': city,
                    'country': country
                }
            )
            count += 1
        except Exception as e:
            print(f"Error saving airport {item.get('iata_code')}: {e}")
            continue
    print(f"Saved {count} airports to DB.")

def save_flights_to_db(flights_data):
    for flight in flights_data:
        dep = flight.get("departure", {})
        arr = flight.get("arrival", {})
        airline = flight.get("airline", {})
        f_info = flight.get("flight", {})
        
        flight_num = f_info.get("iata")
        if not flight_num:
            continue

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
    
