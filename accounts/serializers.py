from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken
from .utils import generate_otp, send_otp_email
from .models import OTPVerification, Profile

User = get_user_model()

class SignupSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    phone_number = serializers.CharField(max_length=20, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Email already registered.")
        return value
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("confirm_password")

        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],  
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            phone_number=validated_data.get('phone_number', ''),
            role=validated_data.get('role', ''),
            is_active=False,  
        )

        Profile.objects.update_or_create(
            user=user,
            defaults={
                "phone_number": validated_data.get("phone_number", ""),
                "role": validated_data.get("role", ""),
            }
        )

        otp = generate_otp()
        OTPVerification.objects.update_or_create(user=user, defaults={"otp": otp})

        send_otp_email(user.email, otp)

        return {"message": "User created. OTP sent to email."}

class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    first_name = serializers.CharField(source="user.first_name", read_only=True)
    last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = ("email", "first_name", "last_name", "phone_number", "role", "photo")
        extra_kwargs = {"photo": {"required": False}}
        read_only_fields = ("email", "first_name", "last_name")
    
    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})
        if "first_name" in user_data:
            instance.user.first_name = user_data["first_name"]
        if "last_name" in user_data:
            instance.user.last_name = user_data["last_name"]
        instance.user.save()
        return super().update(instance, validated_data)

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if not email or not password:
            raise serializers.ValidationError("Both email and password are required.")

        user = authenticate(request=self.context.get('request'), email=email, password=password)

        if not user:
            user = authenticate(request=self.context.get('request'), username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid email or password.")

        if not user.is_active:
            raise serializers.ValidationError("Account is inactive. Complete signup or verify OTP.")

        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        refresh = RefreshToken.for_user(user)
        return {
            "message":"Login successfully",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }

class VerifyOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, attrs):
        try:
            user = User.objects.get(email__iexact=attrs['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        try:
            otp_obj = OTPVerification.objects.get(user=user)
        except OTPVerification.DoesNotExist:
            raise serializers.ValidationError({"otp": "OTP not found."})

        if otp_obj.otp != attrs['otp']:
            raise serializers.ValidationError({"otp": "Invalid OTP."})

        if otp_obj.expires_at < timezone.now():
            raise serializers.ValidationError({"otp": "OTP expired."})
        attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        user.is_active = True
        user.save()

        OTPVerification.objects.filter(user=user).delete()

        refresh = RefreshToken.for_user(user)
        return {
            "message": "OTP verified successfully. User activated.",
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }
