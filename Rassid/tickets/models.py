from django.db import models
from django.contrib.auth import get_user_model
from airports.models import Airport

User = get_user_model()

class Ticket(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    createdBy = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_tickets")
    assignedTo = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tickets")

    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50)
    priority = models.CharField(max_length=20)
    status = models.CharField(max_length=20)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    comment = models.TextField()
    commentedAt = models.DateTimeField(auto_now_add=True)