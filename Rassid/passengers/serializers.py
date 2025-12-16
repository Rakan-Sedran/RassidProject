from rest_framework import serializers
from .models import Passenger, PassengerFlight

class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = "__all__"

class PassengerFlightSerializer(serializers.ModelSerializer):
    passenger = PassengerSerializer(read_only=True)

    class Meta:
        model = PassengerFlight
        fields = "__all__"
