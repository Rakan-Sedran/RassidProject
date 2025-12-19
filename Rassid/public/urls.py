from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="public_home"),
    path("about/", views.about, name="public_about"),
    path("airports/", views.airports_list, name="public_airports_list"),
    path("flights/", views.flights_list, name="public_flights_list"),
]
