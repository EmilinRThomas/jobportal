from django.contrib import admin
from .models import Profile, OTPVerification

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "role", "created_at")
    search_fields = ("user__email", "user__first_name", "user__last_name", "phone_number", "role")

