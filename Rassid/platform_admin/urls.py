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
    path("airports/<int:id>/renew/", views.renew_subscription, name="renew_subscription"),
    path("airports/<int:id>/modify-plan/", views.modify_subscription_plan, name="modify_subscription_plan"),
    path("airports/<int:id>/toggle-status/", views.toggle_subscription_status, name="toggle_subscription_status"),
    path('users/<int:user_id>/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('users/<int:user_id>/toggle-access/', views.admin_toggle_user_access, name='admin_toggle_user_access'),
    path('users/<int:user_id>/delete/', views.delete_user, name='admin_delete_user'),
    path('tickets/<str:ticket_id>/close/', views.admin_close_ticket, name='admin_close_ticket'),
    path("subscriptions/", views.subscriptions, name="platform_admin_subscriptions"),
    path("system-errors/", views.system_errors, name="platform_admin_system_errors"),
]