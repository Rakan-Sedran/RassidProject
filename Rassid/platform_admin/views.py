from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from airports.models import Airport, AirportSubscription
from flights.models import Flight
from tickets.models import Ticket


@login_required
def dashboard(request):
    """
    Platform admin main dashboard
    Template: platform_admin/dashboard.html
    """
    airports_count = Airport.objects.count()
    subscriptions_count = AirportSubscription.objects.count()
    flights_count = Flight.objects.count()
    tickets_count = Ticket.objects.count()

    context = {
        "airports_count": airports_count,
        "subscriptions_count": subscriptions_count,
        "flights_count": flights_count,
        "tickets_count": tickets_count,
    }
    return render(request, "platform_admin/dashboard.html", context)


@login_required
def airports(request):
    """
    List of all airports
    Template: platform_admin/airports.html
    """
    airports_qs = Airport.objects.all().order_by("code")
    return render(request, "platform_admin/airports.html", {
        "airports": airports_qs,
    })


@login_required
def subscriptions(request):
    """
    List of airport subscriptions
    Template: platform_admin/subscriptions.html
    """
    subs = AirportSubscription.objects.select_related("airport").all()
    return render(request, "platform_admin/subscriptions.html", {
        "subscriptions": subs,
    })


@login_required
def system_errors(request):
    """
    System errors / logs page
    Template: platform_admin/system_errors.html
    """
    errors = []
    return render(request, "platform_admin/system_errors.html", {
        "errors": errors,
    })
