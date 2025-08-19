from django.shortcuts import render
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import SignupSerializer,LoginSerializer,VerifyOtpSerializer

# Create your views here.
class SignupView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data=serializer.save()
        return Response(
            data,
            status=status.HTTP_201_CREATED
        )

class VerifyOtpView(generics.GenericAPIView):
    serializer_class = VerifyOtpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)

class LoginView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)