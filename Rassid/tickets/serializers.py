from rest_framework import serializers
from .models import Ticket, TicketLog

class TicketLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketLog
        fields = "__all__"

class TicketSerializer(serializers.ModelSerializer):
    logs = TicketLogSerializer(many=True, read_only=True)

    class Meta:
        model = Ticket
        fields = "__all__"
