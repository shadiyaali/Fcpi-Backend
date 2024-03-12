from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from .helpers import *
import uuid 
from django.contrib import messages,auth 
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.contrib.auth import authenticate 
from rest_framework.authtoken.models import Token
 

class RegisterView(APIView):
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                email = serializer.validated_data.get('email')

                if User.objects.filter(email=email).exists():
                    user = User.objects.get(email=email) 
                    if user.is_email_verified:
                        return Response({'status': 400, 'error': 'User with this email has already been verified'}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        email_sent = send_otp_to_email(user.email, user)
                        if email_sent:
                            return Response({'status': 200, 'message': 'An OTP sent to your email for verification'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'status': 500, 'error': 'Failed to send OTP to email. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                else:
               
                    user = serializer.save()
                    email_sent = send_otp_to_email(user.email, user)
                    if email_sent:
                        return Response({'status': 200, 'message': 'An OTP sent to your email for verification'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'status': 500, 'error': 'Failed to send OTP to email. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'status': 400, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(e)
            return Response({'status': 500, 'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
class VerifyOtp(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')   
            otp = data.get('otp', '').strip()
        
            print("Received email:", email)
            print("Received OTP:", otp)

             
            cached_otp = cache.get(email)
            if cached_otp is None:
                return Response({'status': 403, 'error': 'OTP expired or not found'})

           
            if otp == str(cached_otp):
                 
                cache.delete(email)

              
                try:
                    user_obj = User.objects.get(email__iexact=email)
                    user_obj.is_email_verified = True
                    user_obj.save()
                    return Response({'status': 200, 'message': 'OTP verified successfully'})
                except User.DoesNotExist:
                    return Response({'status': 400, 'error': 'User not found'})
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

         
            if cache.get(email):
                cache.delete(email)

         
            new_otp = random.randint(1000, 9999)
            cache.set(email, new_otp, timeout=60)

            print("New OTP to be sent:", new_otp)

            subject = "OTP Resent"
            message = f"Your new OTP for email verification is: {new_otp}"
            send_mail(subject, message, None, [email])

            return Response({'status': 200, 'message': 'OTP resent successfully'})

        except Exception as e:
            print("Error resending OTP:", e)
            return Response({'status': 500, 'error': 'Something went wrong'})
        
        
class LoginView(APIView):
    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')
            
            print("Email:", email)
            print("Password:", password)
            
            if not email or not password:
                print("Email or password is missing")
                return Response({'status': 400, 'error': 'Email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
            
            print("Attempting login with email:", email ,password)
            
    
            user = auth.authenticate(request, email=email, password=password)
            
            if user is not None:
                print("Authentication successful")
        
                return Response({'status': 200, 'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                print("Authentication failed")
              
                return Response({'status': 400, 'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error in LoginView:", e)
            return Response({'status': 500, 'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    