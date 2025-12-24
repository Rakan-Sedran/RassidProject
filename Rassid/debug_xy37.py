import os
import django
import sys
from datetime import timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rassid.settings')
django.setup()

from django.utils import timezone
from flights.models import Flight, GateAssignment

def debug_flight():
    flight_num = "XY37"
    print(f"--- Debugging Flight {flight_num} ---")
    
    flight = Flight.objects.filter(flightNumber=flight_num).first()
    if not flight:
        print("Flight not found!")
        return

    print(f"Current Status: '{flight.status}'")
    
    gate = GateAssignment.objects.filter(flight=flight).order_by('-assignedAt').first()
    if not gate:
        print("No Gate Assignment found.")
        return
        
    now = timezone.now()
    print(f"Timezone Now: {now}")
    print(f"Boarding Open Time: {gate.boardingOpenTime}")
    
    if gate.boardingOpenTime:
        diff = (now - gate.boardingOpenTime).total_seconds()
        print(f"Seconds since open: {diff}")
        
        if now >= gate.boardingOpenTime:
            print("CONDITION MET: now >= boardingOpenTime")
        else:
            print("CONDITION FAILED: now < boardingOpenTime")
            
    # Replicating the exact query
    matches = Flight.objects.filter(
        flightNumber=flight_num,
        status__iexact='scheduled',
        gateassignment__boardingOpenTime__lte=now
    )
    
    print(f"\nQuery Match Check: {matches.count()} found.")
    if matches.exists():
        print(">> THE QUERY WORKS. The issue is operational (Celery not running/scheduling).")
    else:
        print(">> THE QUERY FAILS. Let's look closer at the filter.")
        # Check sub-condtions
        print(f"Status match 'scheduled'?: {flight.status.lower() == 'scheduled'}")

if __name__ == "__main__":
    debug_flight()
