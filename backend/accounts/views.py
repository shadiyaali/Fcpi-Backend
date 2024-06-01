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
from admins.models import Certificates,Event,SingleEvent
from admins.serializers import EventListSerializer,SingleEventsSerializer
 
 
 

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
            # print("Profile Data:", profile_data)
            
         
            user_instance = User.objects.get(pk=user.pk)
            user_serializer = UserSerializer(user_instance)
            user_data = user_serializer.data
            # print("User Data:", user_data)
 
            response_data = {
                'user': user_data,
                'profile': profile_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
          
            user_instance = User.objects.get(pk=user.pk)
            user_serializer = UserSerializer(user_instance)
            user_data = user_serializer.data
            # print("User Data:", user_data)
            return Response({'user': user_data}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
from rest_framework.exceptions import ValidationError

 

 
 
 

class FeedbackCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        print("Received data:", request.data)

        single_event_day = request.data.get('singleEvent_day')
        event_id = request.data.get('event_id')

        if not single_event_day:
            return Response({'error': 'singleEvent_day is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not event_id:
            return Response({'error': 'event_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        single_event_queryset = SingleEvent.objects.filter(day=single_event_day, event_id=event_id)
        if single_event_queryset.count() == 0:
            return Response({'error': 'SingleEvent does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        elif single_event_queryset.count() > 1:
            return Response({'error': 'Multiple SingleEvent instances found. Please provide more details to uniquely identify the event.'}, status=status.HTTP_400_BAD_REQUEST)

        single_event_instance = single_event_queryset.first()
        print("SingleEvent ID:", single_event_instance.id)

         
        request.data['single_event'] = single_event_instance.id

        serializer = FeedbackSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)

            existing_feedback = Feedback.objects.filter(user=request.user, single_event=single_event_instance).first()
            print("Existing feedback:", existing_feedback)

            if existing_feedback:
                serializer = FeedbackSerializer(existing_feedback, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            else:
               
                serializer.save(user=request.user, single_event=single_event_instance)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

                                                                                                                                                              

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from django.urls import reverse
 

from django.utils import timezone

 

class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        feedbacks = Feedback.objects.filter(user=user)

        if not feedbacks.exists():
            return Response({"message": "No feedback found for the user"}, status=status.HTTP_404_NOT_FOUND)

        serialized_certificates = []

        for feedback in feedbacks:
            single_event = feedback.single_event
            event_name = single_event.event.event_name
            certificates = Certificates.objects.filter(event__event_name=event_name)

            if certificates.exists():
                certificate = certificates.first()
                serialized_certificates.append({
                    "event_name": event_name,
                    "event_date": single_event.date,
                    "single_event": {
                        "points": single_event.points,
                        "day": single_event.day
                    },
                    "certificate_image": certificate.image.url
                })

        print("pppp", serialized_certificates)
        return Response(serialized_certificates, status=status.HTTP_200_OK)




class AuthenticatedUserView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserlistSerializer(user)
        
        return Response(serializer.data)
    
    
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserProfileAPIView(APIView):
    def post(self, request, user_id):
        print("Request data:", request.data)
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
            user = user_profile.user  # Get the related User object

            if request.data:
                # Update UserProfile
                serializer = UserProfileSerializer(user_profile, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()

                    # Update User object with first name and last name
                    user.first_name = request.data.get('first_name', user.first_name)
                    user.last_name = request.data.get('last_name', user.last_name)
                    user.save()

                    return Response(serializer.data, status=status.HTTP_200_OK)
                else:
                    print("Serializer errors:", serializer.errors)
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer = UserProfileSerializer(user_profile)
            print("Profile Data:", serializer.data)
            print("User Data:", {'id': user.id, 'first_name': user.first_name, 'last_name': user.last_name, 'email': user.email, 'phone': user.phone})
            return Response(serializer.data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            return Response({"message": "User profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            print("EEE", e)
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class EnrollEvent(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        user = request.user
        
        if Enrolled.objects.filter(user=user, event=event).exists():
            return Response({"detail": "You are already enrolled in this event."}, status=status.HTTP_400_BAD_REQUEST)
        
        enrollment_data = {'user': user.id, 'event': event.id}
        serializer = EnrolledSerializer(data=enrollment_data)
        if serializer.is_valid():
            serializer.save()
            
            event.is_enrolled = True
            event.save()
            
            subject = 'Enrollment Confirmation'
            message = f'Hello {user.first_name} {user.last_name}\n\nYou have successfully enrolled in the event: {event.event_name}.\n\nThank you!'
            from_email = settings.EMAIL_HOST_USER   
            to_email = [user.email]
            send_mail(subject, message, from_email, to_email)
            
            return Response({"detail": "Successfully enrolled in the event."}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CheckEnrollmentView(APIView):
    def get(self, request, slug):
        if not request.user.is_authenticated:
            return Response({"enrolled": False}, status=status.HTTP_401_UNAUTHORIZED)
        
        event = get_object_or_404(Event, slug=slug)
        user = request.user
        is_enrolled = Enrolled.objects.filter(user=user, event=event).exists()
        
        return Response({"enrolled": is_enrolled})
    
from datetime import datetime  

  


class UserEnrolledEventListView(APIView):
    def calculate_event_dates(self, event):
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def get_event_status(self, event):
        current_date = datetime.now().date()
        start_date, end_date = self.calculate_event_dates(event)
        if start_date and end_date:
            if current_date <= end_date:
                return "Live" if current_date >= start_date else "Upcoming"
            else:
                return "Completed"
        return "Upcoming"

    def get(self, request, user_id):
        user = get_object_or_404(User, id=user_id)

        # Fetch enrolled events for the user
        enrolled_events = Enrolled.objects.filter(user=user).select_related('event')

        events_data = []

        # Categorize events based on their status
        for enrollment in enrolled_events:
            event = enrollment.event
            event_status = self.get_event_status(event)
            event_data = EventListSerializer(event).data
            event_data['status'] = event_status
            events_data.append(event_data)

        return Response({
            'events': events_data
        })
from django.contrib.auth.hashers import make_password

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')
            confirm_password = serializer.validated_data.get('confirm_password')

            # Check if the new password and confirmation password match
            if new_password != confirm_password:
                return Response({'error': 'New password and confirmation password do not match.'}, status=status.HTTP_400_BAD_REQUEST)

           
            request.user.password = make_password(new_password)
            request.user.save()
            
            return Response({'message': 'Password changed successfully.'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class EventPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_feedback = Feedback.objects.filter(user=request.user)
            single_events = [feedback.single_event for feedback in user_feedback]
            serializer = SingleEventsSerializer(single_events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
class SingleUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.is_authenticated:
       
            user = request.user
            serializer = UserSerializer(user)
            return Response(serializer.data)
        else:
            
            return Response({'error': 'User is not authenticated'}, status=status.HTTP_401_UNAUTHORIZED)