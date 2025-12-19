from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="platform_admin_dashboard"),
    path("airports/", views.airports, name="platform_admin_airports"),
    path("subscriptions/", views.subscriptions, name="platform_admin_subscriptions"),
    path("system-errors/", views.system_errors, name="platform_admin_system_errors"),
]
