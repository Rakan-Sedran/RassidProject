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
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse

from django.db.models import Count, Q
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

    last_24h = timezone.now() - timedelta(hours=24)
    emails_sent_count = EmailLog.objects.filter(status='Sent', sent_at__gte=last_24h).count()
    emails_failed_count = EmailLog.objects.filter(status='Failed', sent_at__gte=last_24h).count()

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
        "active_subscriptions": AirportSubscription.objects.filter(status='active').values('airport').distinct().count(),
        "employees_count": User.objects.filter(role__in=['airport_admin', 'airport_staff']).count(),
        "passengers_today": passengers_today,
        "emails_delivered": emails_sent_count,
        "api_errors": emails_failed_count, 
        "system_uptime": system_uptime,
    }

    latest_airports = list(Airport.objects.all().order_by('-created_at')[:5])
    for airport in latest_airports:
        airport.admins_count = User.objects.filter(airport_id=airport.id, role='airport_admin').count()
        sub = AirportSubscription.objects.filter(airport_id=airport.id).order_by('-expire_at').first()
        airport.status = sub.status if sub else 'inactive'
        
        airport.remaining_time_str = "-"
        if sub and sub.expire_at:
            if timezone.is_aware(sub.expire_at):
                now = timezone.now()
            else:
                now = datetime.now()
            
            delta = sub.expire_at - now
            total_days = delta.days

            if total_days > 0:
                years = total_days // 365
                days = total_days % 365
                
                parts = []
                if years > 0:
                    parts.append(f"{years} {'Year' if years == 1 else 'Years'}")
                if days > 0:
                    parts.append(f"{days} {'Day' if days == 1 else 'Days'}")
                
                airport.remaining_time_str = ", ".join(parts) if parts else "Expires Today"
            else:
                airport.remaining_time_str = "Expired"

    tickets = Ticket.objects.filter(status__in=['open', 'in_progress']).order_by('-createdAt')[:5]

    context = {
        "stats": stats,
        "latest_airports": latest_airports,
        "tickets": tickets
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
    
    if sub_req.status not in ['pending', 'approved_pending_payment']:
        messages.warning(request, "This request has already been processed or is fully active.")
        return redirect('admin_requests_list')

    try:
        if User.objects.filter(email=sub_req.admin_email).exists():
            messages.error(request, f"Review Failed: A user with email {sub_req.admin_email} already exists.")
            return redirect('admin_requests_list')

        sub_req.status = 'approved_pending_payment'
        sub_req.reviewed_by = request.user
        sub_req.save()

        checkout_url = request.build_absolute_uri(reverse('airport_payment_checkout', args=[sub_req.id]))

        subject = "Application Approved - Activation Payment Required"
        context = {
            'airport_name': sub_req.airport_name,
            'checkout_url': checkout_url
        }
        
        html_message = render_to_string('emails/payment_request.html', context)
        plain_message = strip_tags(html_message)

        try:
            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [sub_req.admin_email],
                html_message=html_message,
                fail_silently=False
            )
            
            EmailLog.objects.create(
                recipient=sub_req.admin_email,
                subject="Payment Request",
                status="Sent"
            )
            messages.success(request, f"Application for {sub_req.airport_name} approved! Payment request email sent to applicant.")
            
        except Exception as email_error:
            EmailLog.objects.create(
                recipient=sub_req.admin_email,
                subject="Payment Request",
                status="Failed",
                error_message=str(email_error)
            )
            messages.warning(request, f"Approved, but failed to send email: {email_error}")
        
    except Exception as e:
        transaction.set_rollback(True)
        messages.error(request, f"System Error: {str(e)}")
        
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
    admin_users = User.objects.filter(airport_id=airport.id, role='airport_admin')
    
    context = {
        'airport': airport,
        'subscription': subscription,
        'admin_users': admin_users,
    }
    return render(request, 'platform_admin/airport_details.html', context)

@login_required
def renew_subscription(request, id):
    if not is_super_admin(request.user):
        return redirect('public_home')
        
    subscription = AirportSubscription.objects.filter(airport_id=id).order_by('-expire_at').first()
    if not subscription:
        messages.error(request, "No subscription found for this airport.")
        return redirect('admin_airport_details', id=id)
    
    if subscription.expire_at:
        subscription.expire_at = subscription.expire_at + timedelta(days=365)
    else:
        subscription.expire_at = datetime.now() + timedelta(days=365)
        
    subscription.status = 'active'
    subscription.save()
    
    messages.success(request, f"Subscription renewed for {subscription.airport.name} successfully!")
    return redirect_back(request, anchor='subscription-section')

@login_required
def modify_subscription_plan(request, id):
    if not is_super_admin(request.user):
        return redirect('public_home')
        
    airport = get_object_or_404(Airport, id=id)
    subscription = AirportSubscription.objects.filter(airport_id=id).order_by('-expire_at').first()
    
    if not subscription:
         messages.error(request, "No active subscription found to modify.")
         return redirect('admin_airport_details', id=id)

    if request.method == 'POST':
        new_plan = request.POST.get('plan_type')
        if new_plan in ['1_year', '3_years', '5_years']:
            subscription.plan_type = new_plan
            
            duration_days = 365
            if new_plan == '3_years':
                duration_days = 365 * 3
            elif new_plan == '5_years':
                duration_days = 365 * 5
                
            subscription.expire_at = datetime.now() + timedelta(days=duration_days)
            subscription.status = 'active'
            subscription.save()
            
            messages.success(request, f"Plan modified to {new_plan.replace('_', ' ').title()} successfully.")
            return redirect('admin_airport_details', id=id)

    context = {
        'airport': airport,
        'subscription': subscription,
        'plans': SubscriptionRequest.PLAN_CHOICES
    }
    return render(request, 'platform_admin/modify_plan.html', context)

@login_required
def toggle_subscription_status(request, id):
    if not is_super_admin(request.user):
        return redirect('public_home')
    
    airport = get_object_or_404(Airport, id=id)
    subscription = AirportSubscription.objects.filter(airport_id=id).order_by('-expire_at').first()
    
    if not subscription:
        messages.error(request, "No subscription found for this airport.")
        return redirect('admin_airport_details', id=id)
    
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
def delete_user(request, user_id):
    if not is_super_admin(request.user):
        return redirect('public_home')
        
    target_user = get_object_or_404(User, id=user_id)
    email = target_user.email
    
    if target_user == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect_back(request, anchor='admin-section')

    target_user.delete()
    messages.success(request, f"User {email} has been permanently deleted.")
    
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