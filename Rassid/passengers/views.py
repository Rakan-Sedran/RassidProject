from django.shortcuts import render, get_object_or_404
from flights.models import Flight, FlightStatusHistory
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

def tracking(request, flight_id=None):
    if flight_id:
        flight = get_object_or_404(Flight, id=flight_id)
        history = FlightStatusHistory.objects.filter(flight=flight).order_by('-changedAt')
        context = {'flight': flight, 'history': history, 'view_mode': 'detail'}
    else:
        flights = Flight.objects.all().order_by('scheduledDeparture')
        
        cutoff_time = timezone.now() - timedelta(hours=1)
        flights = flights.filter(scheduledDeparture__gte=cutoff_time)
        
        query = request.GET.get('q')
        if query:
            flights = flights.filter(
                Q(flightNumber__icontains=query) |
                Q(origin__code__icontains=query) |
                Q(destination__code__icontains=query)
            )
            
        status_filter = request.GET.get('status')
        if status_filter and status_filter != 'all':
            flights = flights.filter(status__iexact=status_filter)


        origin_city_filter = request.GET.get('origin_city')
        if origin_city_filter and origin_city_filter != 'all':
            flights = flights.filter(origin__city__iexact=origin_city_filter)


        available_cities = Flight.objects.values_list('origin__city', flat=True).distinct().order_by('origin__city')
            
        context = {
            'flights': flights, 
            'view_mode': 'list',
            'search_query': query,
            'status_filter': status_filter,
            'origin_city_filter': origin_city_filter,
            'available_cities': available_cities
        }

    return render(request, 'passengers/tracking.html', context)
