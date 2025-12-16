from rest_framework import serializers
from .models import Airport, AirportSubscription, AirportUser

class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = "__all__"

class AirportSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportSubscription
        fields = "__all__"

class AirportUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirportUser
        fields = "__all__"
