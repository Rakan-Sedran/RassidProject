from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PassengerViewSet, PassengerFlightViewSet
from . import views

router = DefaultRouter()
router.register("passengers", PassengerViewSet)
router.register("passenger-flights", PassengerFlightViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("tracking/", views.tracking, name="passengers_tracking"),
]
