from rest_framework_simplejwt.tokens import RefreshToken
import random
from django.core.mail import send_mail
from django.utils.timezone import now, timedelta
from .models import OTP

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def generate_otp():
    """Generate a 6-digit random OTP"""
    return str(random.randint(100000, 999999))

def send_otp(email):
    """Generate and send OTP via email"""
    otp_code = generate_otp()

    # Delete old OTPs for this email
    OTP.objects.filter(email=email).delete()

    # Save new OTP in the database
    OTP.objects.create(email=email, otp_code=otp_code)

    # Send OTP via email
    send_mail(
        "Your OTP Code",
        f"Your OTP code is {otp_code}. It is valid for 5 minutes.",
        "your-email@example.com",  # Replace with your sender email
        [email],
        fail_silently=False,
    )

    return otp_code  # ✅ Return OTP for testing (remove this in production)
