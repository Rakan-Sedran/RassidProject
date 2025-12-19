from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Passenger, PassengerFlight
from .serializers import PassengerSerializer, PassengerFlightSerializer
from users.permissions import IsAirportAdmin, IsOperator


class PassengerViewSet(ModelViewSet):
    queryset = Passenger.objects.all()
    serializer_class = PassengerSerializer
    permission_classes = [IsAuthenticated, IsOperator]

class PassengerFlightViewSet(ModelViewSet):
    queryset = PassengerFlight.objects.all()
    serializer_class = PassengerFlightSerializer
    permission_classes = [IsAuthenticated, IsOperator]

def tracking(request):
    return render(request, "passengers/tracking.html")
