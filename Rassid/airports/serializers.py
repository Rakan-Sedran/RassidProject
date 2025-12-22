from rest_framework import serializers
from .models import Airport, AirportSubscription, SubscriptionRequest

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = 'all'

class AirportSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportSubscription
        fields = 'all'

class SubscriptionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionRequest
        fields = 'all'