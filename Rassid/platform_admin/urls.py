from django.urls import path
from . import views

urlpatterns = [
    path("", views.admin_dashboard, name="platform_dashboard"),

    path("requests/", views.subscription_requests_list, name="admin_requests_list"),
    path("requests/<int:request_id>/", views.request_details, name="admin_request_details"),
    path("requests/<int:request_id>/approve/", views.approve_request, name="admin_approve_request"),
    path("requests/<int:request_id>/reject/", views.reject_request, name="admin_reject_request"),
    
    path("airports/", views.airports, name="platform_admin_airports"),
    
    path("airports/<int:id>/", views.airport_details, name="admin_airport_details"),

    path("subscriptions/", views.subscriptions, name="platform_admin_subscriptions"),
    path("system-errors/", views.system_errors, name="platform_admin_system_errors"),
]