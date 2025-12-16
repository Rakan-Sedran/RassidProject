from django.db import models
from airports.models import Airport

class Flight(models.Model):
    flightNumber = models.CharField(max_length=20)
    status = models.CharField(max_length=50)
    scheduledDeparture = models.DateTimeField()
    scheduledArrival = models.DateTimeField()
    airlineCode = models.CharField(max_length=10)

    origin = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='origin_flights')
    destination = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name='destination_flights')

    def __str__(self):
        return self.flightNumber


class GateAssignment(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    gateCode = models.CharField(max_length=10)
    terminal = models.CharField(max_length=10)

    boardingOpenTime = models.DateTimeField()
    boardingCloseTime = models.DateTimeField()

    assignedAt = models.DateTimeField(auto_now_add=True)
    releasedAt = models.DateTimeField(null=True, blank=True)


class FlightStatusHistory(models.Model):
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    oldStatus = models.CharField(max_length=50)
    newStatus = models.CharField(max_length=50)
    changedAt = models.DateTimeField(auto_now_add=True)


class FlightAPIImport(models.Model):
    providerName = models.CharField(max_length=50)
    rawPayload = models.TextField()
    importedAt = models.DateTimeField(auto_now_add=True)
