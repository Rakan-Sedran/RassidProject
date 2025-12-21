from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.db import transaction
from datetime import timedelta
import random
import string

from airports.models import Airport, AirportSubscription, SubscriptionRequest
from flights.models import Flight
from tickets.models import Ticket

User = get_user_model()

def is_super_admin(user):
    return user.is_authenticated and user.is_superuser

@login_required
def admin_dashboard(request):
    if not is_super_admin(request.user):
        return redirect('public_home')

    airports_count = Airport.objects.count()
    subscriptions_count = AirportSubscription.objects.count()
    flights_count = Flight.objects.count()
    tickets_count = Ticket.objects.count()
    pending_requests = SubscriptionRequest.objects.filter(status='pending').count()

    context = {
        "airports_count": airports_count,
        "subscriptions_count": subscriptions_count,
        "flights_count": flights_count,
        "tickets_count": tickets_count,
        "pending_requests": pending_requests,
    }
    return render(request, "platform_admin/dashboard.html", context)

@login_required
def subscription_requests_list(request):
    if not is_super_admin(request.user):
        return redirect('public_home')
    
    requests = SubscriptionRequest.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'platform_admin/requests_list.html', {'requests': requests})

@login_required
def request_details(request, request_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    
    sub_req = get_object_or_404(SubscriptionRequest, id=request_id)
    return render(request, 'platform_admin/request_details.html', {'req': sub_req})

@login_required
@transaction.atomic
def approve_request(request, request_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
        
    sub_req = get_object_or_404(SubscriptionRequest, id=request_id)
    
    if sub_req.status != 'pending':
        messages.warning(request, "This request has already been processed.")
        return redirect('admin_requests_list')

    try:
        if User.objects.filter(email=sub_req.admin_email).exists():
            messages.error(request, "A user with this email already exists.")
            return redirect('admin_requests_list')

        print(f"DEBUG: Creating airport for {sub_req.airport_name}...")
        airport = Airport.objects.create(
            name=sub_req.airport_name,
            code=sub_req.airport_code,
            city=sub_req.city,
            country=sub_req.country
        )
        print("DEBUG: Airport created.")

        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        print("DEBUG: Creating user...")
        user = User.objects.create_user(
            email=sub_req.admin_email,
            password=password,
            role='airport_admin',
            airport_id=airport.id
        )
        print("DEBUG: User created.")
        
        years = 1
        if sub_req.selected_plan == '3_years':
            years = 3
        elif sub_req.selected_plan == '5_years':
            years = 5
            
        start_date = timezone.now()
        end_date = start_date + timedelta(days=365*years)
        
        AirportSubscription.objects.create(
            airport=airport,
            plan_type=sub_req.get_selected_plan_display(),
            start_at=start_date,
            expire_at=end_date,
            status='active'
        )

        sub_req.status = 'approved'
        sub_req.reviewed_by = request.user
        sub_req.save()

        subject = "Welcome to RASSID Platform - Your Account is Ready!"
        message = f"""
Dear Partner,

Congratulations! Your airport {airport.name} has been approved.

Here are your login credentials:
URL: {request.build_absolute_uri('/login/')}
Email: {sub_req.admin_email}
Password: {password}

Please login and change your password immediately.

Regards,
RASSID Team
"""
        print("DEBUG: Sending email...")
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [sub_req.admin_email], fail_silently=False)
        print("DEBUG: Email sent.")

        messages.success(request, f"Airport {airport.name} approved and credentials sent!")
        
    except Exception as e:
        # Rollback any DB changes if something fails (e.g. creating User or sending email)
        print(f"DEBUG: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        transaction.set_rollback(True)
        messages.error(request, f"Error: {str(e)}")
        
    return redirect('admin_requests_list')

@login_required
def reject_request(request, request_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
        
    sub_req = get_object_or_404(SubscriptionRequest, id=request_id)
    sub_req.status = 'rejected'
    sub_req.reviewed_by = request.user
    sub_req.save()
    
    try:
        send_mail(
            "Update on your RASSID Subscription Request",
            f"Dear Applicant,\n\nUnfortunately, we could not approve your request for {sub_req.airport_name} at this time.\nPlease contact support for more details.",
            settings.DEFAULT_FROM_EMAIL,
            [sub_req.admin_email],
            fail_silently=False
        )
    except:
        pass

    messages.info(request, "Request has been rejected.")
    return redirect('admin_requests_list')

@login_required
def airports(request):
    if not is_super_admin(request.user):
        return redirect('public_home')
    airports_qs = Airport.objects.all().order_by("code")
    return render(request, "platform_admin/airports.html", {
        "airports": airports_qs,
    })

@login_required
def subscriptions(request):
    if not is_super_admin(request.user):
        return redirect('public_home')
    subs = AirportSubscription.objects.select_related("airport").all()
    return render(request, "platform_admin/subscriptions.html", {
        "subscriptions": subs,
    })

@login_required
def system_errors(request):
    if not is_super_admin(request.user):
        return redirect('public_home')
    errors = []
    return render(request, "platform_admin/system_errors.html", {
        "errors": errors,
    })