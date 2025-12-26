from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Flight, GateAssignment, FlightStatusHistory
from .serializers import (
    FlightSerializer,
    GateAssignmentSerializer,
    FlightStatusHistorySerializer,
)
from users.permissions import IsAirportAdmin, IsOperator
from airports.models import Airport
from django.utils import timezone
from django.db.models import Prefetch


class FlightViewSet(ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    permission_classes = [IsAuthenticated, IsAirportAdmin]


class GateAssignmentViewSet(ModelViewSet):
    queryset = GateAssignment.objects.all()
    serializer_class = GateAssignmentSerializer
    permission_classes = [IsAuthenticated, IsAirportAdmin]


class FlightStatusHistoryViewSet(ModelViewSet):
    queryset = FlightStatusHistory.objects.all()
    serializer_class = FlightStatusHistorySerializer
    permission_classes = [IsAuthenticated, IsOperator]


@login_required
@login_required
def flights_list(request):
    """
    Operator flights list page
    Template: flights/operator/flights_list.html
    """
    if request.user.role != 'operator' or not request.user.airport_id:
        return render(request, "flights/operator/flights_list.html", {"flights": []})

    today = timezone.now().date()
    
    flights = Flight.objects.filter(
        origin_id=request.user.airport_id
    ).prefetch_related(
        Prefetch('gateassignment_set', queryset=GateAssignment.objects.order_by('-assignedAt'), to_attr='latest_gates')
    ).order_by("scheduledDeparture")
    
    destinations = Airport.objects.filter(
        id__in=flights.values_list('destination_id', flat=True).distinct()
    ).order_by('city')

    search_query = request.GET.get('search')
    if search_query:
        flights = flights.filter(flightNumber__icontains=search_query)

    destination_id = request.GET.get('destination')
    if destination_id:
        flights = flights.filter(destination_id=destination_id)

    date_filter = request.GET.get('date')
    if date_filter:
        flights = flights.filter(scheduledDeparture__date=date_filter)

    from tickets.models import Ticket
    from tickets.forms import TicketForm
    
    my_tickets = Ticket.objects.filter(createdBy=request.user).order_by('-createdAt')
    ticket_form = TicketForm()

    total_flights_count = flights.count()

    return render(request, "flights/operator/flights_list.html", {
        "flights": flights,
        "total_flights_count": total_flights_count,
        "search_query": search_query,
        "destinations": destinations,
        "selected_destination": int(destination_id) if destination_id else None,
        "selected_date": date_filter,
        "my_tickets": my_tickets,
        "ticket_form": ticket_form,
    })


@login_required
def edit_flight(request, pk):
    """
    Edit / view single flight
    Template: flights/operator/edit_flight.html
    """
    flight = get_object_or_404(Flight, pk=pk)

    if request.user.role != 'operator' or not request.user.airport_id:
         return redirect('public_home')
    
    if flight.origin_id != request.user.airport_id:
         messages.error(request, "You do not have permission to edit this flight.")
         return redirect('operator_flights_list')

    gate_assignment = GateAssignment.objects.filter(flight=flight).order_by('-assignedAt').first()

    if request.method == 'POST':
        old_status = flight.status
        new_status = request.POST.get('status')
        
        if new_status and new_status != old_status:
            flight.status = new_status
            FlightStatusHistory.objects.create(
                flight=flight,
                oldStatus=old_status,
                newStatus=new_status
            )
        
        dep_time = request.POST.get('scheduledDeparture')
        if dep_time:
            flight.scheduledDeparture = dep_time
        
        flight.is_protected = True
        flight.save()

        gate_code = request.POST.get('gateCode')
        terminal = request.POST.get('terminal')
        boarding_open = request.POST.get('boardingOpenTime')
        boarding_close = request.POST.get('boardingCloseTime')

        if gate_code and terminal:
            GateAssignment.objects.create(
                flight=flight,
                gateCode=gate_code,
                terminal=terminal,
                boardingOpenTime=boarding_open if boarding_open else None, 
                boardingCloseTime=boarding_close if boarding_close else None
            )

        messages.success(request, "Flight details updated successfully.")
        return redirect('operator_flights_list')

    return render(request, "flights/operator/edit_flight.html", {
        "flight": flight,
        "gate_assignment": gate_assignment
    })


@login_required
def passenger_list(request, pk):
    """
    Passengers list for specific flight
    Template: flights/operator/passenger_list.html
    """
    flight = get_object_or_404(Flight, pk=pk)
    
    if request.user.role != 'operator' or flight.origin_id != request.user.airport_id:
         return redirect('operator_flights_list')

    try:
        from passengers.models import PassengerFlight
        passenger_flights = PassengerFlight.objects.filter(flight=flight).select_related('passenger')
    except ImportError:
        passenger_flights = []

    return render(request, "flights/operator/passenger_list.html", {
        "flight": flight,
        "passenger_flights": passenger_flights,
    })

@login_required
def fetch_flights(request):
    """
    Manually trigger flight data fetch
    """
    if request.user.role != 'operator' or not request.user.airport_id:
         messages.error(request, "Permission denied")
         return redirect('public_home')
         
    try:
        from .tasks import update_flights_task
        
        airport = Airport.objects.get(id=request.user.airport_id)
        
        update_flights_task(airport_code=airport.code) 
        
        messages.success(request, f"Flight data fetched successfully for {airport.code}.")
    except Airport.DoesNotExist:
         messages.error(request, "Operator airport not found.")
    except Exception as e:
        messages.error(request, f"Error fetching data: {str(e)}")
        
    return redirect('operator_flights_list')
