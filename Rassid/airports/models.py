from django.db import models
import os

def airport_docs_path(instance, filename):
    return f'airport_docs/{instance.airport_name}/{filename}'

class Airport(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=10, unique=True)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default='Saudi Arabia')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class SubscriptionRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    PLAN_CHOICES = (
        ('1_year', '1 Year License'),
        ('3_years', '3 Years License'),
        ('5_years', '5 Years License'),
    )

    airport_name = models.CharField(max_length=200)
    airport_code = models.CharField(max_length=10)
    country = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    admin_email = models.EmailField()
    admin_phone = models.CharField(max_length=20)
    selected_plan = models.CharField(max_length=50, choices=PLAN_CHOICES, default='1_year')
    
    official_license = models.FileField(upload_to=airport_docs_path)
    commercial_record = models.FileField(upload_to=airport_docs_path, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request: {self.airport_name} ({self.status})"

class AirportSubscription(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=50) 
    start_at = models.DateTimeField()
    expire_at = models.DateTimeField()
    max_employees = models.IntegerField(default=10)
    status = models.CharField(max_length=20, default='active')

    def __str__(self):
        return f"{self.airport.code} - {self.plan_type}"