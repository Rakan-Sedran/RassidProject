from django.contrib import admin
from .models import Airport, AirportSubscription, SubscriptionRequest

admin.site.register(Airport)
admin.site.register(AirportSubscription)
admin.site.register(SubscriptionRequest)