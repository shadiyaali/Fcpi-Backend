from django.core.mail import send_mail
from django.core.cache import cache
import random
from django.core.mail import send_mail 
import jwt
from django.conf import settings
import json
 

def send_otp_to_email(email,data):
    print(data)
    if cache.get(email):
        return False

    try:
        otp_to_sent = random.randint(1000, 9999)
    
        payload = {
                        'phone_number': data['phone'],
                        'first_name': data['first_name'],
                        'last_name':  data['last_name'],
                        'email':  data['email'],
                        'password':  data['password'],
                        'otp': otp_to_sent
                    }
        
        key =  payload['email']
        serialized_payload = json.dumps(payload)
        if_set = settings.REDIS.set(key, serialized_payload)
        subject = "OTP Verification"
        message = f"Your OTP for email verification is: {otp_to_sent}"
        send_mail(subject, message, None, [email])
        return True
    except Exception as e:
        print(e)
        return False


def forgot_otp_to_email(email, user):
    if cache.get(email):
        return False  

    try:
        otp_to_sent = random.randint(1000, 9999)

        payload = {
            'phone': user.phone,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'password': user.password,  
            'otp': otp_to_sent
        }

        serialized_payload = json.dumps(payload)

        key = payload['email']
        settings.REDIS.set(key, serialized_payload)

        subject = "OTP Verification"
        message = f"Your OTP for email verification is: {otp_to_sent}"

        send_mail(subject, message, None, [email])

        return True
    except Exception as e:
        print(f"Error sending OTP to {email}: {e}")
        return False