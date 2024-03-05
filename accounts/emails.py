from django.core.mail import send_mail
import random
from django.conf import settings
from .models import User, OTPVerification
from datetime import timedelta
from django.utils import timezone


def generate_otp(user):
    otp_code = str(random.randint(100000, 999999))
    expiration_time = timezone.now() + timedelta(minutes=5)
    OTPVerification.objects.create(user=user, otp=otp_code, expiration_time=expiration_time)
    return otp_code


def send_otp_via_mail(email):
    subject = "zobspaze email verfication"
    user_obj = User.objects.get(email=email)
    otp = generate_otp(user_obj)
    message = f'Your zobspaze otp is {otp} , This expires in 5 minutes'
    email_from = settings.EMAIL_HOST
    send_mail(subject, message, email_from, [email])