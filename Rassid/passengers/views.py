from django.shortcuts import render, get_object_or_404, redirect
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Passenger, PassengerFlight
from .serializers import PassengerSerializer, PassengerFlightSerializer
from users.permissions import IsAirportAdmin, IsOperator
from django.utils import timezone
from flights.models import FlightStatusHistory, GateAssignment
import os
import requests
from django.http import JsonResponse
from django.views.decorators.http import require_GET

# Placeholder mapping: User must verify Building/Floor IDs for KKIA.
# Structure: Terminal Code -> {'building_id': X, 'default_floor_id': Y}
TERMINAL_API_MAP = {
    '1': {'building_id': '201', 'default_floor_id': '1'},  # Example IDs
    '2': {'building_id': '202', 'default_floor_id': '1'},
    '3': {'building_id': '203', 'default_floor_id': '1'},
    '4': {'building_id': '204', 'default_floor_id': '1'},
    '5': {'building_id': '205', 'default_floor_id': '1'},
    'T1': {'building_id': '201', 'default_floor_id': '1'},
    'T2': {'building_id': '202', 'default_floor_id': '1'},
    'T3': {'building_id': '203', 'default_floor_id': '1'},
    'T4': {'building_id': '204', 'default_floor_id': '1'},
    'T5': {'building_id': '205', 'default_floor_id': '1'},
}

BASE_MAP_API_URL = "https://mapsapi.kkia.sa/api/public/v1/buildings"

class PassengerViewSet(ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [IsAuthenticated, IsOperator]

class PassengerFlightViewSet(ModelViewSet):
    queryset = PassengerFlight.objects.all()
    serializer_class = PassengerFlightSerializer
    permission_classes = [IsAuthenticated, IsOperator]

def tracking(request):
    return render(request, "passengers/tracking.html")

def flight_tracker(request, booking_token):
    """
    Specific Flight Tracking page.
    Accessible via secure Booking UUID (PassengerFlight.access_token).
    """
    # Strict Access: Fetch proper reservation or 404
    p_flight = get_object_or_404(PassengerFlight, access_token=booking_token)
    
    passenger = p_flight.passenger
    flight = p_flight.flight
    
    timeline = []
    
    status_history = FlightStatusHistory.objects.filter(flight=flight).order_by('changedAt')
    for h in status_history:
        timeline.append({
            'type': 'status',
            'timestamp': h.changedAt,
            'title': f"Status Changed to {h.newStatus}",
            'description': f"Flight status updated from {h.oldStatus} to {h.newStatus}"
        })
        
    gate_history = GateAssignment.objects.filter(flight=flight).order_by('assignedAt')
    for g in gate_history:
        timeline.append({
            'type': 'gate',
            'timestamp': g.assignedAt,
            'title': f"Gate Assigned: {g.gateCode}",
            'description': f"Terminal {g.terminal}. Boarding: {g.boardingOpenTime.strftime('%H:%M') if g.boardingOpenTime else 'TBD'}"
        })
        
    timeline.sort(key=lambda x: x['timestamp'], reverse=True)
    
    current_gate = gate_history.last()
    
    total_seconds_open = 0
    total_seconds_close = 0
    phase = "unknown"
    
    if current_gate and current_gate.boardingOpenTime and current_gate.boardingCloseTime:
        now = timezone.now()
        open_time = current_gate.boardingOpenTime
        close_time = current_gate.boardingCloseTime
        
        if now < open_time:
            phase = "pre_open"
            total_seconds_open = int((open_time - now).total_seconds())
        elif now < close_time:
            phase = "boarding"
            total_seconds_close = int((close_time - now).total_seconds())
        else:
            phase = "closed"

    def format_time(seconds):
        if seconds < 0: return "00:00:00"
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{h:02d}:{m:02d}"

    
    # Map Integration Logic
    mapbox_token = os.getenv('MAPBOX_ACCESS_TOKEN', '')
    
    # Determine Building and Floor IDs based on Terminal
    terminal_code = str(current_gate.terminal) if (current_gate and current_gate.terminal) else "5" # Default to T5
    
    # fallback for raw terminal string if not in GateAssignment
    if not terminal_code and flight and flight.origin.code == 'RUH': 
        # Logic to guess terminal from gate code if needed, but for now rely on GateAssignment
        pass

    # Clean terminal code (remove 'Terminal ' prefix if exists)
    terminal_key = terminal_code.replace('Terminal ', '').strip()
    
    mapping = TERMINAL_API_MAP.get(terminal_key, TERMINAL_API_MAP['5']) # Default to T5
    
    building_id = mapping['building_id']
    floor_id = mapping['default_floor_id']
    
    # Start URL for correct floor
    # We will pass the IDs to the frontend so it can construct the Proxy URL
    
    return render(request, "passengers/tracker.html", {
        "passenger": passenger,
        "flight": flight,
        "timeline": timeline,
        "gate": current_gate,
        "now": timezone.now(),
        "phase": phase,
        "seconds_to_open": total_seconds_open,
        "seconds_to_close": total_seconds_close,
        "formatted_open": format_time(total_seconds_open),
        "formatted_close": format_time(total_seconds_close),
        "mapbox_access_token": mapbox_token,
        "map_building_id": building_id,
        "map_floor_id": floor_id,
        "map_terminal_key": terminal_key,
    })

@require_GET
def map_proxy(request):
    """
    Proxy request to KKIA Maps API to avoid CORS.
    Expects 'building_id' and 'floor_id' query params.
    """
    building_id = request.GET.get('building_id')
    floor_id = request.GET.get('floor_id')
    
    if not building_id or not floor_id:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
        
    url = f"{BASE_MAP_API_URL}/{building_id}/floors/{floor_id}/pois"
    
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return JsonResponse(response.json(), safe=False)
    except requests.RequestException as e:
        return JsonResponse({'error': str(e)}, status=502)
