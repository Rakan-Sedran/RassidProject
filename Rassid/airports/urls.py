from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AirportViewSet, AirportSubscriptionViewSet, SubscriptionRequestViewSet, 
    dashboard, employees_list, add_employee, airport_settings, 
    request_subscription, approve_subscription,edit_employee, delete_employee,
)

router = DefaultRouter()
router.register("list", AirportViewSet)
router.register("subscriptions", AirportSubscriptionViewSet)
router.register("requests", SubscriptionRequestViewSet)

urlpatterns = [
    path("api/", include(router.urls)),

    path('register/', request_subscription, name='request_subscription'),

    path('admin/approve/<int:request_id>/', approve_subscription, name='approve_subscription'),

    path("dashboard/", dashboard, name="airport_dashboard"),
    
    path("employees/", employees_list, name="airport_admin_employees"),
    path("employees/add/", add_employee, name="airport_admin_add_employee"),
    path("employees/edit/<int:employee_id>/",edit_employee, name="airport_admin_edit_employee"),
    path("employees/delete/<int:employee_id>/", delete_employee, name="airport_admin_delete_employee"),
    path("settings/", airport_settings, name="airport_settings"), 
]