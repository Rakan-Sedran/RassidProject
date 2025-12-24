from celery import shared_task
from .services.flights_api import fetch_flights
from .models import Flight, Airport

@shared_task
def update_flights_task(airport_code=None):
    data = fetch_flights(airport_code=airport_code)
    if not data or "data" not in data:
        return

    # Use the service function to handle parsing and saving
    # This avoids duplication and ensures model consistency
    from .services.flights_api import save_flights_to_db
    save_flights_to_db(data["data"])
    
    # --- Automated Status Updates (Boarding/Final Call) ---
    check_and_update_flight_statuses(airport_code)

def check_and_update_flight_statuses(airport_code=None):
    from django.utils import timezone
    from datetime import timedelta
    from .models import Flight, FlightStatusHistory
    
    now = timezone.now()
    
    # 1. Auto-Boarding: Scheduled -> Boarding
    # Logic: If status is 'scheduled' AND now >= boardingOpenTime
    flights_to_board = Flight.objects.filter(
        status__iexact='scheduled',
        gateassignment__boardingOpenTime__lte=now
    ).exclude(status__iexact='boarding') # Safety exclude
    
    if airport_code:
        flights_to_board = flights_to_board.filter(origin__code=airport_code)
        
    for flight in flights_to_board:
        print(f"Auto-updating {flight.flightNumber} to Boarding")
        old_status = flight.status
        flight.status = 'Boarding'
        flight.save()
        
        # Log history (Signal will trigger email)
        FlightStatusHistory.objects.create(
            flight=flight,
            oldStatus=old_status,
            newStatus='Boarding'
        )

    # 2. Auto-Final Call: Boarding -> Final Call
    # Logic: If status is 'boarding' AND now >= boardingCloseTime - 10 mins
    # We want to catch flights that are closing soon but aren't yet closed
    # This runs every minute, so simple inequality checks work well
    
    flights_final_call = Flight.objects.filter(
        status__iexact='boarding',
        gateassignment__boardingCloseTime__lte=now + timedelta(minutes=10)
    ).exclude(status__iexact='final call')
    
    if airport_code:
        flights_final_call = flights_final_call.filter(origin__code=airport_code)
        
    for flight in flights_final_call:
        print(f"Auto-updating {flight.flightNumber} to Final Call")
        old_status = flight.status
        flight.status = 'Final Call'
        flight.save()
        
        # Log history (Signal will trigger email)
        FlightStatusHistory.objects.create(
            flight=flight,
            oldStatus=old_status,
            newStatus='Final Call'
        )
    
    # --- Hardcoded Passenger Logic (User Request) ---
    create_and_link_test_passengers(airport_code)

def check_1hr_departure_reminders(airport_code=None):
    from django.utils import timezone
    from datetime import timedelta
    from .models import Flight
    from passengers.signals import send_update_email_to_passengers
    
    now = timezone.now()
    # Window: Flights departing between 60 mins and 61 mins from now (to avoid double sending, assuming 1 min cron)
    # Ideally tracking "reminded" state in DB is better, but this is a simple requested logic
    start_window = now + timedelta(minutes=60)
    end_window = now + timedelta(minutes=62) # slightly wider
    
    flights = Flight.objects.filter(
        scheduledDeparture__gte=start_window,
        scheduledDeparture__lt=end_window,
    ).exclude(status__in=['landed', 'cancelled', 'departed'])
    
    if airport_code:
        flights = flights.filter(origin__code=airport_code)
        
    for flight in flights:
        print(f"Sending 1hr reminder for {flight.flightNumber}")
        send_update_email_to_passengers(
            flight,
            title_en="Upcoming Departure",
            desc_en=f"Your flight {flight.flightNumber} departs in 1 hour. Please head to your gate.",
            title_ar="اقتراب موعد المغادرة",
            desc_ar=f"رحلتك {flight.flightNumber} تغادر خلال ساعة. يرجى التوجه إلى البوابة."
        )

def create_and_link_test_passengers(airport_code=None):
    from passengers.models import Passenger, PassengerFlight
    import random
    import string

    # 1. Define the 3 requested passengers
    test_passengers = [
        {"fullName": "Ziyad Alzahrani", "phone": "+966535778335", "email": "zsyz6279@gmail.com", "preferredLanguage": "ar"},
        {"fullName": "Rakan Alyami", "phone": "+966509835558", "email": "srakan595@gmail.com", "preferredLanguage": "ar"},
        {"fullName": "Abdulrahman Alqahtani", "phone": "+966505510181", "email": "aaq_224@hotmail.com", "preferredLanguage": "ar"},
    ]

    saved_passengers = []
    for p_data in test_passengers:
        passenger, created = Passenger.objects.get_or_create(
            email=p_data["email"],
            defaults={
                "fullName": p_data["fullName"],
                "phone": p_data["phone"],
                "preferredLanguage": p_data["preferredLanguage"]
            }
        )
        saved_passengers.append(passenger)
        if created:
            print(f"Created passenger: {passenger.fullName}")

    # 2. Get Flights to link to
    if airport_code:
        flights = Flight.objects.filter(origin__code=airport_code, status__iexact="scheduled")
    else:
        flights = Flight.objects.filter(status__iexact="scheduled")

    # 3. Link Passengers
    for flight in flights:
        for passenger in saved_passengers:
            # Check if already linked
            if not PassengerFlight.objects.filter(passenger=passenger, flight=flight).exists():
                # Generate dummy seat and reference
                row = random.randint(1, 30)
                col = random.choice(['A', 'B', 'C', 'D', 'E', 'F'])
                seat = f"{row}{col}"
                ref = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                
                PassengerFlight.objects.create(
                    passenger=passenger,
                    flight=flight,
                    seatNumber=seat,
                    bookingRef=ref,
                    ticketStatus="Checked-in"
                )
                print(f"Linked {passenger.fullName} to {flight.flightNumber}")
