import random
from django.core.mail import send_mail
from django.conf import settings

def generate_otp(length=4) -> str:
    return ''.join(random.choices('0123456789', k=length))

def send_otp_email(to_email: str, otp: str):
    subject = "Your OTP Code"
    message = f"Your OTP is: {otp}. It expires in 10 minutes."
    from_email = settings.DEFAULT_FROM_EMAIL
    print(f"DEBUG: OTP for {to_email} -> {otp}")

    send_mail(subject, message, from_email, [to_email], fail_silently=True)