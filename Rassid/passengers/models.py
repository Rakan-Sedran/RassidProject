from django.db import models
from flights.models import Flight

class Passenger(models.Model):
    fullName = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    trackingToken = models.CharField(max_length=200)
    preferredLanguage = models.CharField(max_length=10, default="en")

    def __str__(self):
        return self.fullName


class PassengerFlight(models.Model):
    passenger = models.ForeignKey(Passenger, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)

    seatNumber = models.CharField(max_length=10)
    bookingRef = models.CharField(max_length=20)
    ticketStatus = models.CharField(max_length=20)
