from django.db import models
from passengers.models import PassengerFlight

class Notification(models.Model):
    passengerFlight = models.ForeignKey(PassengerFlight, on_delete=models.CASCADE)
    channel = models.CharField(max_length=10, default="email")   
    content = models.TextField()
    status = models.CharField(max_length=20)  
    errorMessage = models.TextField(null=True, blank=True)
    sentAt = models.DateTimeField(auto_now_add=True)
