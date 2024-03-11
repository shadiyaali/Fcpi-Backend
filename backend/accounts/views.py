from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from .helpers import *
import uuid  
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from rest_framework import status



class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')
                
             
                if User.objects.filter(email=email, is_email_verified=True).exists():
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'error': 'User with this email has already been verified'})
                
              
                if User.objects.filter(email=email).exists():
                    return Response({'status': status.HTTP_400_BAD_REQUEST, 'error': 'User with this email already exists. Please verify your email.'})
                
                user = serializer.save()
                email_sent = send_otp_to_email(user.email, user)
                if email_sent:
                    return Response({'status': status.HTTP_200_OK, 'message': 'An OTP sent to your email for verification'})
                else:
                    return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error': 'Failed to send OTP to email. Please try again later.'})
            else:
                return Response({'status': status.HTTP_400_BAD_REQUEST, 'errors': serializer.errors})
        except Exception as e:
            print(e)
            return Response({'status': status.HTTP_500_INTERNAL_SERVER_ERROR, 'error': 'Something went wrong'})


        
        
class VerifyOtp(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')   
            otp = data.get('otp', '').strip()
        
            print("Received email:", email)  
            print("Received OTP:", otp)  

            try:
              
                user_obj = User.objects.get(email__iexact=email)
            except User.DoesNotExist:
      
                serializer = UserSerializer(data={'email': email})
                if serializer.is_valid():
                    user_obj = serializer.save()
                else:
                    return Response({'status': 400, 'error': 'Failed to create a new user'})

         
            if otp == str(user_obj.otp):
                user_obj.is_email_verified = True
                user_obj.save()
                return Response({'status': 200, 'message': 'OTP verified successfully'})
            else:
                return Response({'status': 403, 'error': 'Invalid OTP'})
        
        except Exception as e:
            print("Error:", e)
            return Response({'status': 500, 'error': 'Something went wrong'})
        
        
class ResendOtp(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')

            if email is None:
                return Response({'status': 400, 'error': 'Email parameter is missing or invalid'})

            if not cache.get(email):
                return Response({'status': 400, 'error': 'No OTP sent for this email'})

            otp_to_sent = random.randint(1000, 9999)
            cache.set(email, otp_to_sent, timeout=60)

            print("OTP to be sent:", otp_to_sent)
            print("Type of OTP to be sent:", type(otp_to_sent))

            subject = "OTP Resent"
            message = f"Your new OTP for email verification is: {otp_to_sent}"
            send_mail(subject, message, None, [email])

            return Response({'status': 200, 'message': 'OTP resent successfully'})

        except Exception as e:
            print("Error resending OTP:", e)
            return Response({'status': 500, 'error': 'Something went wrong'})
        
        
class ResendOtp(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')

            if email is None:
                return Response({'status': 400, 'error': 'Email parameter is missing or invalid'})

            if not cache.get(email):
                return Response({'status': 400, 'error': 'No OTP sent for this email'})

            otp_to_sent = random.randint(1000, 9999)
            cache.set(email, otp_to_sent, timeout=60)

            print("OTP to be sent:", otp_to_sent)
            print("Type of OTP to be sent:", type(otp_to_sent))

            subject = "OTP Resent"
            message = f"Your new OTP for email verification is: {otp_to_sent}"
            send_mail(subject, message, None, [email])

            return Response({'status': 200, 'message': 'OTP resent successfully'})

        except Exception as e:
            print("Error resending OTP:", e)
            return Response({'status': 500, 'error': 'Something went wrong'})
    