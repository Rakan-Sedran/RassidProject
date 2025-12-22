from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.db import transaction
from datetime import timedelta, datetime
import random
import string

from airports.models import Airport, AirportSubscription, SubscriptionRequest
from flights.models import Flight
from tickets.models import Ticket
from passengers.models import PassengerFlight
from notifications.models import EmailLog

User = get_user_model()

def is_super_admin(user):
    return user.is_authenticated and user.is_superuser

def redirect_back(request, fallback='platform_dashboard', anchor=''):
    referer = request.META.get('HTTP_REFERER', fallback)
    if anchor:
        if '#' in referer:
            referer = referer.split('#')[0]
        return redirect(f"{referer}#{anchor}")
    return redirect(referer)

@login_required
def admin_dashboard(request):
    if not is_super_admin(request.user):
        return redirect('public_home')

    emails_sent_count = EmailLog.objects.filter(status='Sent').count()
    emails_failed_count = EmailLog.objects.filter(status='Failed').count()

    today = timezone.now().date()
    passengers_today = PassengerFlight.objects.filter(
        flight__scheduledDeparture__date=today
    ).count()

    total_ops = emails_sent_count + emails_failed_count
    if total_ops > 0 and emails_failed_count > 0:
        uptime_calc = ((total_ops - emails_failed_count) / total_ops) * 100
        system_uptime = f"{uptime_calc:.1f}%"
    else:
        system_uptime = "100%"

    stats = {
        "airports_count": Airport.objects.count(),
        "active_subscriptions": AirportSubscription.objects.filter(status='active').count(),
        "employees_count": User.objects.filter(role='airport_staff').count(),
        "passengers_today": passengers_today,
        "emails_delivered": emails_sent_count,
        "api_errors": emails_failed_count,
        "system_uptime": system_uptime
    }

    latest_airports = Airport.objects.all().order_by('-id')[:5]
    admins = User.objects.filter(role='airport_admin')[:5]
    

    recent_tickets = Ticket.objects.select_related('airport').all().order_by('-createdAt')[:5]
 

    context = {
        "stats": stats,
        "latest_airports": latest_airports,
        "admins": admins,
        "tickets": recent_tickets
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

        airport = Airport.objects.create(
            name=sub_req.airport_name,
            code=sub_req.airport_code,
            city=sub_req.city,
            country=sub_req.country
        )

        password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        user = User.objects.create_user(
            email=sub_req.admin_email,
            password=password,
            role='airport_admin',
            airport_id=airport.id
        )
        
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
        try:
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [sub_req.admin_email], fail_silently=False)
            
            EmailLog.objects.create(
                recipient=sub_req.admin_email,
                subject="Account Approval",
                status="Sent"
            )
            messages.success(request, f"Airport {airport.name} approved and credentials sent!")
            
        except Exception as email_error:
            EmailLog.objects.create(
                recipient=sub_req.admin_email,
                subject="Account Approval",
                status="Failed",
                error_message=str(email_error)
            )
            messages.warning(request, f"Airport approved, BUT email failed to send. Error: {email_error}")
        
    except Exception as e:
        transaction.set_rollback(True)
        messages.error(request, f"Error: {str(e)}")
        
    return redirect('admin_requests_list')

@login_required
def reject_request(request, request_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    sub_req = get_object_or_404(SubscriptionRequest, id=request_id)

    if request.method == 'POST':
        reason = request.POST.get('reason', '').strip()
        to_email = request.POST.get('email', sub_req.admin_email).strip() or sub_req.admin_email

        sub_req.status = 'rejected'
        sub_req.reviewed_by = request.user
        sub_req.save()

        subject = "Update on your RASSID Subscription Request"
        message = f"Dear Applicant,\n\nUnfortunately, we could not approve your request for {sub_req.airport_name}.\n\n"
        if reason:
            message += f"Reason provided by admin:\n{reason}\n\n"
        message += "Please contact support for more details.\n\nRegards,\nRASSID Team"

        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [to_email],
                fail_silently=False
            )
            EmailLog.objects.create(
                recipient=to_email,
                subject="Request Rejected",
                status="Sent"
            )
            messages.success(request, "Request rejected and email sent to applicant.")
        except Exception as e:
            EmailLog.objects.create(
                recipient=to_email,
                subject="Request Rejected",
                status="Failed",
                error_message=str(e)
            )
            messages.warning(request, f"Request rejected but email failed to send: {e}")

        return redirect('admin_requests_list')

    # If not POST, redirect back to details page
    return redirect('admin_request_details', request_id)

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

@login_required
def airport_details(request, id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    airport = get_object_or_404(Airport, id=id)
    subscription = AirportSubscription.objects.filter(airport=airport).first()
    admin_user = User.objects.filter(airport_id=airport.id, role='airport_admin').first()
    
    context = {
        'airport': airport,
        'subscription': subscription,
        'admin_user': admin_user,
    }
    return render(request, 'platform_admin/airport_details.html', context)

@login_required
def renew_subscription(request, id):
    if not is_super_admin(request.user):
        return redirect('public_home')
        
    subscription = get_object_or_404(AirportSubscription, airport_id=id)
    
    if subscription.expire_at:
        subscription.expire_at = subscription.expire_at + timedelta(days=365)
    else:
        subscription.expire_at = datetime.now() + timedelta(days=365)
        
    subscription.status = 'active'
    subscription.save()
    
    messages.success(request, f"Subscription renewed for {subscription.airport.name} successfully!")
    return redirect_back(request, anchor='subscription-section')

@login_required
def toggle_subscription_status(request, id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    
    airport = get_object_or_404(Airport, id=id)
    subscription = AirportSubscription.objects.filter(airport=airport).first()
    
    if subscription:
        if subscription.status == 'active':
            subscription.status = 'suspended'
            messages.warning(request, f"Subscription suspended for {airport.name}.")
        else:
            subscription.status = 'active'
            messages.success(request, f"Subscription activated for {airport.name}.")
        subscription.save()
    else:
        messages.error(request, "No subscription found for this airport.")
    
    return redirect_back(request, anchor='subscription-section')

@login_required
def admin_reset_password(request, user_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    
    target_user = get_object_or_404(User, id=user_id)
    new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    target_user.set_password(new_password)
    target_user.save()
    
    messages.success(request, f"Password reset for {target_user.email}. New Password: {new_password}")
    return redirect_back(request, anchor='admin-section')

@login_required
def admin_toggle_user_access(request, user_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    
    target_user = get_object_or_404(User, id=user_id)
    if target_user.is_active:
        target_user.is_active = False
        messages.warning(request, f"User {target_user.email} has been disabled.")
    else:
        target_user.is_active = True
        messages.success(request, f"User {target_user.email} has been enabled.")
    
    target_user.save()
    return redirect_back(request, anchor='admin-section')

@login_required
def admin_close_ticket(request, ticket_id):
    if not is_super_admin(request.user):
        return redirect('public_home')

    try:
        ticket = Ticket.objects.get(id=ticket_id)
        ticket.status = 'closed'
        ticket.save()
        messages.success(request, f"Ticket #{ticket_id} has been closed.")
    except Ticket.DoesNotExist:
        messages.error(request, "Ticket not found.")

    return redirect_back(request)