from django.shortcuts import render
from airports.models import Airport
from flights.models import Flight, GateAssignment

def home(request):
    return render(request, "public/home.html", {
        "flights": Flight.objects.all()[:20]
    })

def about(request):
    return render(request, "public/about.html")

def airports_list(request):
    from airports.models import AirportSubscription, SubscriptionRequest
    from django.utils import timezone
    active_subs = AirportSubscription.objects.filter(status='active', expire_at__gt=timezone.now())
    airports = Airport.objects.filter(id__in=active_subs.values_list('airport_id', flat=True))

    airport_images = {}
    for airport in airports:
        req = SubscriptionRequest.objects.filter(airport_code=airport.code, status='approved').order_by('-created_at').first()
        if req and req.image:
            airport_images[airport.id] = req.image.url
        else:
            airport_images[airport.id] = '/static/img/airport-default.png'

    return render(request, "public/airports_list.html", {"airports": airports, "airport_images": airport_images})

def flights_list(request):
    from users.models import User
    from django.db.models import Q
    from flights.models import GateAssignment

    managed_airport_ids = User.objects.filter(role='airport_admin').values_list('airport_id', flat=True).distinct()
    
    from django.utils import timezone
    from django.db.models import Q
    
    cutoff_time = timezone.now() - timezone.timedelta(hours=1)
    
    
    from django.db.models import Prefetch, Q
    
    flights = Flight.objects.filter(
        origin_id__in=managed_airport_ids
    ).filter(
        Q(status__iexact='active') |
        (
            Q(scheduledDeparture__gte=cutoff_time) & 
            ~Q(status__iexact='landed') & 
            ~Q(status__iexact='cancelled')
        )
    ).select_related('origin', 'destination').prefetch_related(
        Prefetch('gateassignment_set', queryset=GateAssignment.objects.order_by('-assignedAt'), to_attr='latest_gates')
    ).order_by("scheduledDeparture")

    search_query = request.GET.get('search')
    if search_query:
        flights = flights.filter(
            Q(flightNumber__icontains=search_query) |
            Q(destination__city__icontains=search_query) |
            Q(destination__code__icontains=search_query)
        )

    return render(request, "public/flights_list.html", {
        "flights": flights,
        "search_query": search_query
    })

def pricing_view(request):
    return render(request, 'public/pricing.html')

def contact(request):
    if request.method == "POST":
        from django.core.mail import send_mail
        from django.conf import settings
        from django.contrib import messages
        from .models import ContactSubmission
        
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        subject_type = request.POST.get('subject')
        message = request.POST.get('message')
        
        ContactSubmission.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            subject=subject_type,
            message=message
        )
        
        full_subject = f"[contact-us] {subject_type} from {first_name} {last_name}"
        email_body = f"""
        You have received a new contact form submission.

        Name: {first_name} {last_name}
        Email: {email}
        Subject: {subject_type}

        Message:
        {message}
        """
        
        try:
            # Send to the admin/support email
            recipient = settings.EMAIL_HOST_USER if settings.EMAIL_HOST_USER else 'zsyz8335@gmail.com'
            
            send_mail(
                full_subject,
                email_body,
                settings.DEFAULT_FROM_EMAIL,
                [recipient],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent successfully! We will contact you shortly.")
        except Exception as e:
            print(e)
            # Even if email fails, we saved to DB, so we can tell user "received" or just warn
            messages.success(request, "Your message has been recorded. We will contact you shortly.")
            
    return render(request, "public/contact.html")