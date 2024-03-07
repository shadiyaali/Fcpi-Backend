from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.views import APIView
from .helpers import *
import uuid  # Add this import for generating unique UUIDs

class RegisterView(APIView):
    
    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)
            
            if not serializer.is_valid():
                return Response({
                    'status': 403,
                    'errors': serializer.errors
                })
            
            user = serializer.save()
            
            # Send OTP to user's email
            email_sent = send_otp_to_email(user.email, user)
            
            if email_sent:
                
                return Response({'status': 200, 'message': 'An OTP sent to your email for verification'})
            else:
               
                return Response({'status': 500, 'error': 'Failed to send OTP to email. Please try again later.'})
            
        except Exception as e:
            print(e)
            return Response({'status': 500, 'error': 'Something went wrong'})

class VerifyOtp(APIView):
    
    def post(self, request):
        try:
            data = request.data
            user_obj = User.objects.get(email=data['email'])
            otp = data.get('otp')
            
            if user_obj.otp == otp:
                user_obj.is_email_verified = True   
                user_obj.save()
                return Response({'status': 200, 'message': 'Your OTP is verified'})
        
            return Response({'status': 403, 'message': 'Your OTP is wrong'})        
            
        except Exception as e:
            print(e)
            return Response({'status': 500, 'error': 'Something went wrong'})

    def patch(self, request):
        try:
            data = request.data
            
            if not User.objects.filter(email=data.get('email')).exists():
                return Response({'status': 404, 'error': 'No user found with this email'}) 
            
            if send_otp_to_email(data.get('email')):
                return Response({'status': 200, 'message': 'New OTP sent to your email'})   
            
            return Response({'status': 500, 'error': 'Failed to send OTP to email. Please try again later.'}) 
        
        except Exception as e:
            print(e)
            return Response({'status': 500, 'error': 'Something went wrong'})
