from django.core.mail import send_mail
from django.core.cache import cache
import random

def send_otp_to_email(email, user_obj):
    if cache.get(email):
        return False

    try:
        otp_to_sent = random.randint(1000, 9999)
        cache.set(email, otp_to_sent, timeout=60)
        user_obj.otp = otp_to_sent
        user_obj.save()

        # Send OTP to user's email
        subject = "OTP Verification"
        message = f"Your OTP for email verification is: {otp_to_sent}"
        send_mail(subject, message, None, [email])
        return True
    except Exception as e:
        print(e)
        return False
