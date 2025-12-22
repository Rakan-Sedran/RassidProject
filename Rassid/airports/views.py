from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils import timezone

from .models import Airport, AirportSubscription, SubscriptionRequest
from .serializers import AirportSerializer, AirportSubscriptionSerializer, SubscriptionRequestSerializer
from .forms import AirportSignupForm
from users.permissions import IsSuperAdmin
from flights.models import Flight
from tickets.models import Ticket

User = get_user_model()

class AirportViewSet(viewsets.ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

class AirportSubscriptionViewSet(viewsets.ModelViewSet):
    queryset = AirportSubscription.objects.all()
    serializer_class = AirportSubscriptionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

class SubscriptionRequestViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionRequest.objects.all()
    serializer_class = SubscriptionRequestSerializer


def request_subscription(request):
    if request.method == 'POST':
        form = AirportSignupForm(request.POST, request.FILES)
        if form.is_valid():
            subscription = form.save()
            
            subject = f"New Subscription: {subscription.airport_name}"
            
            context = {
                'airport_name': subscription.airport_name,
                'airport_code': subscription.airport_code,
                'city': subscription.city,
                'country': subscription.country,
                'plan': subscription.get_selected_plan_display(),
                'email': subscription.admin_email,
                'phone': subscription.admin_phone, 
                'admin_url': request.build_absolute_uri('/platform-admin/') 
            }

            html_message = render_to_string('emails/new_request.html', context)
            plain_message = strip_tags(html_message)
            
            try:
                send_mail(
                    subject,
                    plain_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL], 
                    html_message=html_message,
                    fail_silently=True
                )
            except:
                pass

            messages.success(request, "Your request has been submitted successfully!")
            return redirect('public_home')
    else:
        initial_plan = request.GET.get('plan', '1_year')
        form = AirportSignupForm(initial={'selected_plan': initial_plan})

    return render(request, 'airports/subscription_request.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role != 'airport_admin' or not request.user.airport_id:
        return redirect('public_home')

    my_airport = get_object_or_404(Airport, id=request.user.airport_id)
    today = timezone.now().date()
    now = timezone.now()

    total_flights = Flight.objects.filter(origin=my_airport).count()
    
    today_flights = Flight.objects.filter(
        origin=my_airport, 
        scheduledDeparture__date=today
    ).count()

    total_tickets = Ticket.objects.filter(airport=my_airport).count()

    upcoming_flights = Flight.objects.filter(
        origin=my_airport,
        scheduledDeparture__gte=now
    ).order_by('scheduledDeparture')[:5]

    context = {
        'airport': my_airport,
        'total_flights': total_flights,
        'today_flights': today_flights,
        'total_tickets': total_tickets,
        'upcoming_flights': upcoming_flights,
    }
    
    return render(request, "airports/dashboard.html", context)

@login_required
def employees_list(request):
    if request.user.role != 'airport_admin':
        return redirect('public_home')
    employees = User.objects.filter(role='operator', airport_id=request.user.airport_id)
    return render(request, "airports/employees_list.html", {"employees": employees})

@login_required
def add_employee(request):
    if request.user.role != 'airport_admin':
        return redirect('public_home')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            User.objects.create_user(
                email=email,
                password=password,
                role='operator',
                airport_id=request.user.airport_id
            )
            return redirect('airport_admin_employees')
        except:
            pass
    return render(request, "airports/add_employee.html")

@login_required
def edit_employee(request, employee_id):
    if request.user.role != 'airport_admin' or not request.user.airport_id:
        return redirect('public_home')

    employee = get_object_or_404(User, id=employee_id)

    if employee.airport_id != request.user.airport_id:
        messages.error(request, "You are not authorized to edit this employee.")
        return redirect('airport_admin_employees')

    if request.method == 'POST':
        employee.first_name = request.POST.get('first_name')
        employee.last_name = request.POST.get('last_name')
        employee.email = request.POST.get('email')
        employee.phone_number = request.POST.get('phone_number')
        
        employee.save()
        messages.success(request, "Employee updated successfully.")
        return redirect('airport_admin_employees')

    my_airport = get_object_or_404(Airport, id=request.user.airport_id)

    context = {
        'employee': employee,
        'airport': my_airport
    }
    return render(request, 'airports/edit_employee.html', context)
@login_required
def delete_employee(request, employee_id):
    if request.user.role != 'airport_admin' or not request.user.airport_id:
        messages.error(request, "Access denied.")
        return redirect('public_home')

    employee = get_object_or_404(User, id=employee_id)

    if employee.airport_id != request.user.airport_id:
        messages.error(request, "You cannot delete an employee from another airport.")
        return redirect('airport_admin_employees')

    if employee.id == request.user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('airport_admin_employees')

    employee.delete()
    messages.success(request, "Employee deleted successfully.")
    
    return redirect('airport_admin_employees')

@login_required
def airport_settings(request):
    if request.user.role != 'airport_admin':
        return redirect('public_home')
    airport_id = request.user.airport_id
    airport = None
    subscription = None
    if airport_id:
        airport = get_object_or_404(Airport, id=airport_id)
        subscription = AirportSubscription.objects.filter(airport=airport).first()
    return render(request, "airports/airport_settings.html", {
        "airport": airport,
        "subscription": subscription,
    })


@login_required
def approve_subscription(request, request_id):
    if not request.user.is_superuser:
        messages.error(request, "Access Denied")
        return redirect('public_home')

    sub_request = get_object_or_404(SubscriptionRequest, id=request_id)

    if sub_request.status == 'approved':
        messages.warning(request, "This request is already approved.")
        return redirect('platform_admin_dashboard')

    try:
        generated_password = get_random_string(length=12)

        if User.objects.filter(email=sub_request.admin_email).exists():
             messages.error(request, "User with this email already exists.")
             return redirect('platform_admin_dashboard')

        new_admin = User.objects.create_user(
            email=sub_request.admin_email,
            password=generated_password,
            first_name=sub_request.admin_name,
            role='airport_admin',
            is_active=True
        )

        new_airport = Airport.objects.create(
            name=sub_request.airport_name,
            code=sub_request.airport_code,
            city=sub_request.city,
            country=sub_request.country
        )

        new_admin.airport_id = new_airport.id 
        new_admin.save()

        AirportSubscription.objects.create(
            airport=new_airport,
            plan=sub_request.selected_plan,
            is_active=True
        )

        sub_request.status = 'approved'
        sub_request.save()

        subject = "Welcome! Your Airport Platform Account is Ready"
        login_url = request.build_absolute_uri('/login/')
        
        context = {
            'admin_name': sub_request.admin_name,
            'airport_name': sub_request.airport_name,
            'email': sub_request.admin_email,
            'password': generated_password,
            'login_url': login_url
        }

        html_message = render_to_string('emails/subscription_approved.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [sub_request.admin_email],
            html_message=html_message,
            fail_silently=False
        )

        messages.success(request, f"Airport {new_airport.name} created and credentials sent to admin.")

    except Exception as e:
        messages.error(request, f"Error approving request: {str(e)}")

    return redirect('platform_admin_dashboard')