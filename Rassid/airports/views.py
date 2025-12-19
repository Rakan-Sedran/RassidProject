from django.shortcuts import render

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .models import Airport, AirportUser, AirportSubscription
from .serializers import (
    AirportSerializer,
    AirportUserSerializer,
    AirportSubscriptionSerializer,
)
from users.permissions import IsSuperAdmin, IsAirportAdmin


class AirportViewSet(ModelViewSet):
    queryset = Airport.objects.all()
    serializer_class = AirportSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]


class AirportUserViewSet(ModelViewSet):
    queryset = AirportUser.objects.all()
    serializer_class = AirportUserSerializer
    permission_classes = [IsAuthenticated, IsAirportAdmin]


class AirportSubscriptionViewSet(ModelViewSet):
    queryset = AirportSubscription.objects.all()
    serializer_class = AirportSubscriptionSerializer
    permission_classes = [IsAuthenticated, IsSuperAdmin]

def dashboard(request):
    """
    Airport admin dashboard page
    Template: airports/admin/dashboard.html
    """
    return render(request, "airports/admin/dashboard.html")


def employees_list(request):
    """
    List of airport employees
    Template: airports/admin/employees_list.html
    """
    employees = AirportUser.objects.all()
    return render(request, "airports/admin/employees_list.html", {
        "employees": employees,
    })


def add_employee(request):
    """
    Add new employee page (form only for now)
    Template: airports/admin/add_employee.html
    """
    return render(request, "airports/admin/add_employee.html")


def airport_settings(request):
    """
    Airport settings page
    Template: airports/admin/airport_settings.html
    """
    airport = Airport.objects.first()
    subscription = None
    if airport:
        subscription = AirportSubscription.objects.filter(airport=airport).first()

    return render(request, "airports/admin/airport_settings.html", {
        "airport": airport,
        "subscription": subscription,
    })
