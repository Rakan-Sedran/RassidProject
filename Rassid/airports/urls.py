from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AirportViewSet, AirportUserViewSet, AirportSubscriptionViewSet
from . import views

router = DefaultRouter()
router.register("airports", AirportViewSet)
router.register("users", AirportUserViewSet)
router.register("subscriptions", AirportSubscriptionViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("dashboard/", views.dashboard, name="airport_admin_dashboard"),
    path("employees/", views.employees_list, name="airport_admin_employees"),
    path("employees/add/", views.add_employee, name="airport_admin_add_employee"),
    path("settings/", views.airport_settings, name="airport_admin_settings"),
]
