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
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from rest_framework.generics import ListAPIView
from rest_framework import generics
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from admins.models import Certificates
from .serializers import CertificategenerateSerializer
 
 

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
               
                    # user = serializer.save()
                
                    email_sent = send_otp_to_email(email,serializer.validated_data)
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
            redis_conn = settings.REDIS

        # Get the key from the request or wherever it's coming from
            key =  email

        # Retrieve the payload from Redis
            payload = redis_conn.get(key)
            print("inside verify",payload) 
            payload_str = payload.decode('utf-8')  # Decode bytes to string
            payload_dict = json.loads(payload_str)  # Parse JSON string to dictionary

 
             
         
    
            otp = payload_dict.get('otp')

         
           
          
            cached_otp =  otp
            if cached_otp is None:
                return Response({'status': 403, 'error': 'OTP expired or not found'})

           
            if otp == cached_otp:                 
                settings.REDIS.delete(email)             
                try:
                    user_data = {
                        'phone': payload_dict.get('phone_number'),
                        'first_name': payload_dict.get('first_name'),
                        'last_name': payload_dict.get('last_name'),
                        'email': payload_dict.get('email'),
                        'password': payload_dict.get('password'),
                        'otp': otp
                    }

                    # Create a serializer instance with the data
                    serializer = UserSerializer(data=user_data)

                    # Validate and save the data
                    if serializer.is_valid():
                        user = serializer.save()
                        user.is_email_verified = True
                        user.save()
                        print("User saved successfully")
                        return Response({'status': 200, 'message': 'OTP verified successfully'})
                 
                   
                       
                    else:
                        print(serializer.errors)
                        return Response(serializer.errors)
                    # user_obj = User.objects.get(email__iexact=email)
                    # user_obj.is_email_verified = True
                    # user_obj.save()
            
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
        
        
 

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        print("rrrrrrrrrrrrrr:",user)
        token['user_id'] = user.id
        print("user_id:", user.id)
        token['username'] = user.first_name  
        return token

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


 
class AddUser(APIView):
    def post(self, request):
        try:            
            serializer = UserSerializer(data=request.data)
            print(request.data)
            if serializer.is_valid():
                user = serializer.save()
                return Response({'status': 200, 'message': 'User added '}, status=status.HTTP_200_OK)
            else:
                return Response({'status': 400, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'status': 500, 'error': 'Something went wrong'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class UserRoleCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UserRoleSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class UserRoleListView(ListAPIView):
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer        
    
class UserListView(APIView):
    def get(self, request):
        users = User.objects.filter(is_staff=False)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    
class UserProfileCreateView(APIView):
  
    def post(self, request, *args, **kwargs):
        try:
            user = request.user

            if UserProfile.objects.filter(user=user).exists():
                return Response({'error': 'User profile already exists'}, status=status.HTTP_400_BAD_REQUEST)

        
            request.data['user'] = user.id

            serializer = UserProfileSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
class updateUser(generics.UpdateAPIView) :
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    
class DeleteUser(generics.DestroyAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer   
    
    
class UserprofileListView(APIView):
      def get(self, request):        
        users = UserProfile.objects.exclude(user__is_superuser=True)      
        serializer = UserProfileSerializer(users, many=True)       
        return Response(serializer.data)
    

class UserProfileView(APIView):
    def get(self, request):
        user = request.user

        try:
            user_profile = UserProfile.objects.get(user=user)
            profile_serializer = UserProfileSerializer(user_profile)
            profile_data = profile_serializer.data  
            print("Profile Data:", profile_data)
            
         
            user_instance = User.objects.get(pk=user.pk)
            user_serializer = UserSerializer(user_instance)
            user_data = user_serializer.data
            print("User Data:", user_data)
 
            response_data = {
                'user': user_data,
                'profile': profile_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
          
            user_instance = User.objects.get(pk=user.pk)
            user_serializer = UserSerializer(user_instance)
            user_data = user_serializer.data
            print("User Data:", user_data)
            return Response({'user': user_data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class FeedbackCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        
        event_id = request.data.get('event')   
        existing_feedback = Feedback.objects.filter(user=request.user, event_id=event_id).exists()
        if existing_feedback:
            return Response({"message": "Feedback already submitted for this event"}, status=status.HTTP_400_BAD_REQUEST)

        # 
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user'] = request.user
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


 


class CertificateImageView(APIView):
    def get(self,user, event_id=None):
        if event_id is None:
            return Response({"error": "Event ID is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            print("Event ID:", event_id) 
            certificate = Certificates.objects.filter(event_id=event_id).first()
            print("Certificate:", certificate)
            if certificate:             
                has_feedback = Feedback.objects.filter(event_id=event_id, user=user).exists()
                print("Has feedback:", has_feedback)
                if has_feedback:
                    serializer = CertificategenerateSerializer(certificate)
                    return Response(serializer.data)
                else:
                    return Response({"error": "Feedback not provided for this event."}, status=status.HTTP_404_NOT_FOUND)
            else:
                return Response({"error": "Certificate not found for this event."}, status=status.HTTP_404_NOT_FOUND)
        except Feedback.DoesNotExist:
            print("Feedback does not exist for this event.")
            return Response({"error": "Feedback not found for this event."}, status=status.HTTP_404_NOT_FOUND)
