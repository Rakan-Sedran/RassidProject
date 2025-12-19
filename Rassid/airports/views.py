from django.shortcuts import render, redirect
from django.contrib import messages
from airports.models import Airport
from users.decorators import custom_login_required
from flights.models import Flight, GateAssignment, FlightStatusHistory
from flights.services.flights_api import fetch_flights, save_flights_to_db 
from users.models import User
from django.http import JsonResponse

def api_sync_flights(request):
    try:
        data = fetch_flights()
        if data and 'data' in data:
            flights_list = data['data']
            save_flights_to_db(flights_list)
            return JsonResponse({'status': 'success', 'count': len(flights_list)})
        return JsonResponse({'status': 'no_data'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

from django.db.models import Q

@custom_login_required
def operator_dashboard(request):
    role = request.session.get('role')
    if role not in ['operator', 'admin', 'platform_admin']:
        messages.error(request, "Access Denied: You are not an operator.")
        return redirect('home')
        
    current_user_id = request.session.get('user_id')
    current_user = User.objects.get(id=current_user_id)
    
    flights = Flight.objects.filter(origin__id=current_user.airportId).order_by('scheduledDeparture')
    
    query = request.GET.get('q')
    if query:
        flights = flights.filter(
            Q(flightNumber__icontains=query) |
            Q(destination__code__icontains=query) |
            Q(destination__city__icontains=query)
        )

    return render(request, 'airports/operator_dashboard.html', {
        'flights': flights,
        'search_query': query,
        'airport': Airport.objects.get(id=current_user.airportId)
    })

@custom_login_required
def admin_dashboard(request):
    role = request.session.get('role')
    if role not in ['admin', 'platform_admin']:
        messages.error(request, "Access Denied: You are not an administrator.")
        return redirect('home')
    
    current_user_id = request.session.get('user_id')
    current_user = User.objects.get(id=current_user_id)
    
    operators = User.objects.filter(role='operator', airportId=current_user.airportId)
    employees_count = operators.count()
    
    flights_count = Flight.objects.all().count() 
    
    flights = Flight.objects.filter(origin__id=current_user.airportId).order_by('scheduledDeparture')
    
    query = request.GET.get('q')
    if query:
        flights = flights.filter(
            Q(flightNumber__icontains=query) |
            Q(destination__code__icontains=query) |
            Q(destination__city__icontains=query)
        )
    
    context = {
        'operators': operators,
        'employees_count': employees_count,
        'flights_count': flights_count,
        'flights': flights, 
        'search_query': query,
        'airport': Airport.objects.get(id=current_user.airportId)
    }
    return render(request, 'airports/admin_dashboard.html', context)

def sync_flights(request):
    try:
        data = fetch_flights()
        if data and 'data' in data:
            save_flights_to_db(data['data'])
            messages.success(request, 'Flights synced successfully from API!')
        else:
            messages.error(request, 'Failed to fetch data from API (Check Key or Limit).')
    except Exception as e:
        messages.error(request, f'Error syncing flights: {str(e)}')
    
    return redirect('operator_dashboard')

def update_gate(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        gate_code = request.POST.get('gate_code')
        terminal = request.POST.get('terminal')
        boarding_open = request.POST.get('boarding_open')
        boarding_close = request.POST.get('boarding_close')
        
        try:
            flight = Flight.objects.get(flightNumber=flight_number)
            
            current_user_id = request.session.get('user_id')
            current_user = User.objects.get(id=current_user_id)
            
            if flight.origin.id != current_user.airportId:
                messages.error(request, "Permission Denied: You can only manage flights from your airport.")
                return redirect('operator_dashboard')

            if not boarding_open: boarding_open = None
            if not boarding_close: boarding_close = None

            flight.gate = gate_code
            flight.terminal = terminal
            flight.boarding_open = boarding_open
            flight.boarding_close = boarding_close
            flight.save()
            
            status_msg = f"Gate changed to {gate_code} (T{terminal})"
            if boarding_open:
                status_msg += f" | Boarding: {boarding_open}"
            
            FlightStatusHistory.objects.create(
                flight=flight,
                oldStatus=f"Update",
                newStatus=status_msg
            )
            
            messages.success(request, f'Flight {flight_number} updated successfully.')
            
            messages.success(request, f'Gate for {flight_number} updated to {gate_code}. Notifications sent to passengers.')
            
        except Flight.DoesNotExist:
            messages.error(request, 'Flight not found.')
        except Exception as e:
            messages.error(request, f'Error updating gate: {str(e)}')
            
        return redirect('operator_dashboard')
        
    return redirect('operator_dashboard')
