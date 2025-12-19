from django.shortcuts import render
from airports.models import Airport
from flights.models import Flight

def home(request):
    return render(request, "public/flights_list.html", {
        "flights": Flight.objects.all()[:20]
    })

def about(request):
    return render(request, "public/about.html")

def airports_list(request):
    airports = Airport.objects.all()
    return render(request, "public/airports_list.html", {"airports": airports})

def flights_list(request):
    flights = Flight.objects.all().order_by("-scheduledDeparture")[:50]
    return render(request, "public/flights_list.html", {"flights": flights})
