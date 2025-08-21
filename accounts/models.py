from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

# Create your models here.
class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not password:
            raise ValueError("Superusers must have a password")

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)

    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, blank=True)

    otp = models.CharField(max_length=6, blank=True)
    otp_created_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  

    objects = UserManager()

    def otp_is_valid(self, minutes=10):
        if not self.otp or not self.otp_created_at:
            return False
        return timezone.now() <= self.otp_created_at + timezone.timedelta(minutes=minutes)

    def __str__(self):
        return self.email

class OTPVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="otps")
    otp = models.CharField(max_length=6)  # store 6-digit OTP
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True) 
    is_verified = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def is_valid(self):
        """Check if OTP is still valid (not expired and not already verified)."""
        return (not self.is_verified) and (self.expires_at >= timezone.now())

    def __str__(self):
        return f"OTP for {self.user.username} - {self.otp}"
    
class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    phone_number = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to="profiles/", blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
       return f"Profile({getattr(self.user, 'email', self.user.pk)})" 
