from django.db import models
from airports.models import AirportUser, Airport

class Ticket(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    createdBy = models.ForeignKey(AirportUser, on_delete=models.CASCADE, related_name="created_tickets")
    assignedTo = models.ForeignKey(AirportUser, on_delete=models.SET_NULL, null=True, blank=True)

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)  
    priority = models.CharField(max_length=20)  
    status = models.CharField(max_length=20)    

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    userId = models.CharField(max_length=100)
    comment = models.TextField()
    commentedAt = models.DateTimeField(auto_now_add=True)
