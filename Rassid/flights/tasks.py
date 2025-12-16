from celery import shared_task
from .services.flights_api import fetch_flights, parse_flight
from .models import Flight, Airport

@shared_task
def update_flights_task():
    data = fetch_flights()
    if not data or "data" not in data:
        return

    for flight_data in data["data"]:
        parsed = parse_flight(flight_data)

        dep_airport, _ = Airport.objects.get_or_create(
            name=parsed["departure_airport"]
        )
        arr_airport, _ = Airport.objects.get_or_create(
            name=parsed["arrival_airport"]
        )

        Flight.objects.update_or_create(
            flight_number=parsed["flight_number"],
            defaults={
                "airline": parsed["airline"],
                "status": parsed["status"],
                "departure_airport": dep_airport,
                "arrival_airport": arr_airport,
                "departure_time": parsed["departure_time"],
                "arrival_time": parsed["arrival_time"],
                "gate": parsed["gate"]
            }
        )
