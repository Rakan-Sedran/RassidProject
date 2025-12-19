from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer

class LoginView(APIView):
    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if not user:
            return Response({"detail": "invalid credentials"}, status=400)
        token = RefreshToken.for_user(user)
        return Response({"access": str(token.access_token), "refresh": str(token)})

class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
