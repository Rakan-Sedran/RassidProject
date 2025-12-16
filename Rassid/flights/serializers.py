from rest_framework import serializers
from .models import Flight, GateAssignment, FlightStatusHistory

class GateAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GateAssignment
        fields = "__all__"

class FlightStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = FlightStatusHistory
        fields = "__all__"

class FlightSerializer(serializers.ModelSerializer):
    gate_assignments = GateAssignmentSerializer(many=True, read_only=True)

    class Meta:
        model = Flight
        fields = "__all__"
