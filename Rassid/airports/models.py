from django.db import models

class Airport(models.Model):
    code = models.CharField(max_length=10)  # IATA
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.code


class AirportSubscription(models.Model):
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)
    planType = models.CharField(max_length=50)
    startAt = models.DateTimeField()
    expireAt = models.DateTimeField()
    maxEmployees = models.IntegerField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.airport.code} - {self.planType}"


class AirportUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=20)  
    airport = models.ForeignKey(Airport, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
