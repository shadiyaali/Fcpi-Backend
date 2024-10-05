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
from admins.models import Certificates,Event,SingleEvent,GeneralEvent,GeneralCertificates
from admins.serializers import EventListSerializer,SingleEventsSerializer ,AdminSerializer,GeneralEventListSerializer, GeneralSingleEventsSerializer
 
 
 

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

       
            key =  email

      
            payload = redis_conn.get(key)
            print("inside verify",payload) 
            payload_str = payload.decode('utf-8')  
            payload_dict = json.loads(payload_str)      
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
          
                    serializer = UserSerializer(data=user_data)
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
        
        
 
from django.utils.translation import gettext_lazy as _ 
import logging
logger = logging.getLogger(__name__)
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User   
 

 

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"No active account found with the given credentials for user {email}.")
            raise serializers.ValidationError(
                {"error": _("No active account found with the given credentials.")},
                code='authentication'
            )

       
        if user.status == 'Inactive':
            logger.warning(f"Inactive account attempted to log in with email {email}.")
            raise serializers.ValidationError(
                {"error": _("This account is inactive.")},
                code='inactive_account'
            )

        if user.is_staff:  
            logger.warning(f"Attempted admin login with user {email}.")
            raise serializers.ValidationError(
                {"error": _("Admin login is not allowed on this page.")},
                code='admin_login'
            )

        if user.password_is_null:
            logger.warning(f"User {email} has null password. Password expired. Please reset your password.")
            raise serializers.ValidationError(
                {"error": _("Password expired. Please reset your password.")},
                code='password_expired'
            )

        user = authenticate(username=email, password=password)
        if user is None:
            logger.warning(f"Incorrect password attempt for user {email}.")
            raise serializers.ValidationError(
                {"error": _("Incorrect password.")},
                code='authentication'
            )

        data = super().validate(attrs)
        data['user_id'] = user.id
        data['username'] = user.first_name
        return data

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
        

# class UserRoleCreateView(APIView):
#     def post(self, request, *args, **kwargs):
#         serializer = UserRoleSerializer(data=request.data)
#         print(request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
# class UserRoleListView(ListAPIView):
#     queryset = UserRole.objects.all()
#     serializer_class = UserRoleSerializer        
    
class UserListView(APIView):
    def get(self, request):
        users = User.objects.filter(is_staff=False)
        serializer = UsersprofileSerializer(users, many=True)
        return Response(serializer.data)

 
    
    
class UserALLListView(APIView):
    def get(self, request):
        try:
            users = User.objects.all()
            profiles = UserProfile.objects.all()
            
            # Create dictionaries for efficient lookups
            user_profiles = {profile.user.id: profile for profile in profiles}
            
            user_data = []
            for user in users:
                user_profile = user_profiles.get(user.id)
                serializer_user = UserSerializer(user)
                serializer_profile = UserProfileSerializer(user_profile) if user_profile else None
                user_data.append({
                    "user": serializer_user.data,
                    "profile": serializer_profile.data if serializer_profile else None
                })
            
            return Response(user_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
class UserAllListView(APIView):
    def get(self, request):
        try:
            users = User.objects.filter(is_staff=False)
            user_profiles = UserProfile.objects.filter(user__in=users)
            user_profiles_serializer = UserProfileSerializer(user_profiles, many=True)
            user_profiles_data = user_profiles_serializer.data
            
            # Fetch user data and serialize
            users_serializer = UserAllSerializer(users, many=True)
            users_data = users_serializer.data

            # Combine user and user profile data
            for user_data in users_data:
                user_profile_data = next((profile for profile in user_profiles_data if profile['user'] == user_data['id']), None)
                user_data['user_profile'] = user_profile_data

            return Response(users_data)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  
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
    def get(self, request, user_id=None):
        print('Received User ID:', user_id)  # Debug print statement

        user = get_object_or_404(User, pk=user_id) if user_id else request.user

        try:
            user_profile = UserProfile.objects.get(user=user)
            profile_serializer = UserProfileSerializer(user_profile)
            profile_data = profile_serializer.data
            
            user_serializer = UserSerializer(user)
            user_data = user_serializer.data
            
            response_data = {
                'user': user_data,
                'profile': profile_data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        except UserProfile.DoesNotExist:
            user_serializer = UserSerializer(user)
            user_data = user_serializer.data
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

        # Check if the user has already submitted feedback for this single event
        existing_feedback = Feedback.objects.filter(user=request.user, single_event=single_event_instance).first()
        if existing_feedback:
            return Response({'error': 'You have already submitted feedback for this event.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FeedbackSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, single_event=single_event_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


                                                                                                                                                              

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from django.urls import reverse
 

from django.utils import timezone

 
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .models import Feedback, Certificates

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
            event = single_event.event
            certificates = Certificates.objects.filter(event=event)

            if certificates.exists():
                certificate = certificates.first()
                event_name = event.event_name
                if event.days > 1:
                    event_name += f" (Day {single_event.day})"

                forum_name = event.forum.title if event.forum else 'N/A'

                # Add the feedback creation date here
                feedback_created_at = feedback.created_at

                serialized_certificates.append({
                    "event_name": event_name,
                    "forum": forum_name,
                    "days": event.days,
                    "event_date": single_event.date,
                    "single_event": {
                        "points": single_event.points,
                        "day": single_event.day
                    },
                    "certificate_image": certificate.image.url,
                    "feedback_created_at": feedback_created_at  # Include the feedback creation date
                })

        return Response(serialized_certificates, status=status.HTTP_200_OK)





class AuthenticatedUserView(APIView):
    def get(self, request):
        user = request.user
        serializer = UserlistSerializer(user)
        
        return Response(serializer.data)
    

 
        
        return Response(serializer.data)   
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class UserProfileAPIView(APIView):
    
    def put(self, request, user_id):
        print("userid",user_id)
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
        
        # Check if the user is already enrolled
        enrollment = Enrolled.objects.filter(user=user, event=event).first()

        if enrollment:
            # If the user is already enrolled, remove them from the enrollment
            enrollment.delete()
            
            event.is_enrolled = False
            event.save()
            
            return Response({"detail": "Successfully unenrolled from the event."}, status=status.HTTP_200_OK)
        else:
            # If the user is not enrolled, proceed to enroll them
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
    permission_classes = [IsAuthenticated]

    def calculate_event_dates(self, event):
        """
        Calculates the start and end dates of the event based on its single events.
        """
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_multi_event_times(self, event):
        """
        Calculates the starting time of the first MultiEvent and ending time of the last MultiEvent
        when days = 1 for the given event.
        """
        single_event = event.single_events.filter(day=1).first()
        if single_event:
            multi_events = single_event.multi_events.all()
            if multi_events.exists():
                start_time = multi_events.first().starting_time
                end_time = multi_events.last().ending_time
                return start_time, end_time
        return None, None

    def get_event_status(self, event):
        """
        Determines the status of the event based on current datetime and multi-event times.
        """
        current_datetime = timezone.now()
        start_date, end_date = self.calculate_event_dates(event)
        start_time, end_time = self.calculate_multi_event_times(event)

        if start_date and end_date and start_time and end_time:
            # Combine date and time to get the full datetime for start and end
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, end_time))

            if current_datetime <= event_end_datetime:
                return "Live" if current_datetime >= event_start_datetime else "Upcoming"
            else:
                return "Completed"
        
        return "Upcoming"

    def get(self, request):
        user = request.user
        enrolled_events = Enrolled.objects.filter(user=user).select_related('event')

        events_data = []
        for enrollment in enrolled_events:
            event = enrollment.event
            event_status = self.get_event_status(event)
            event_data = EventListSerializer(event).data
            event_data['status'] = event_status

            start_date, end_date = self.calculate_event_dates(event)
            if start_date and end_date:
                event_data['start_date'] = start_date.strftime('%Y-%m-%d')
                event_data['end_date'] = end_date.strftime('%Y-%m-%d')
            else:
                event_data['start_date'] = "Invalid date"
                event_data['end_date'] = "Invalid date"

            if event.days == 1:
                start_time, end_time = self.calculate_multi_event_times(event)
                if start_time and end_time:
                    event_data['start_time'] = start_time.strftime('%H:%M:%S')
                    event_data['end_time'] = end_time.strftime('%H:%M:%S')
                else:
                    event_data['start_time'] = "Invalid time"
                    event_data['end_time'] = "Invalid time"
                event_data['end_date'] = None
            else:
                event_data['start_time'] = None
                event_data['end_time'] = None

            events_data.append(event_data)

        return Response({'events': events_data})

    
    
    
from django.contrib.auth.hashers import make_password

class ChangePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            new_password = serializer.validated_data.get('new_password')
            confirm_password = serializer.validated_data.get('confirm_password')

        
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
        
        
 
class UserDetailView(APIView):
    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user_profile = UserProfile.objects.get(user=user)
            serializer_user = UserSerializer(user)
            serializer_profile = UserProfileSerializer(user_profile)
            return Response({"user": serializer_user.data, "profile": serializer_profile.data})
        except (User.DoesNotExist, UserProfile.DoesNotExist):
            return Response({'error': 'User profile does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        
 

        
from django.http import QueryDict        
 
class UserProfileUpdateView(APIView):
    def put(self, request, user_id):
        print("Request data:", request.data)

        try:
            user_profile = UserProfile.objects.get(user__id=user_id)
            print("User profile found:", user_profile)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile does not exist'}, status=status.HTTP_404_NOT_FOUND)

        user_data = request.data.get('user', None)
        print("Extracted user_data:", user_data)

        # Create a copy of the request data
        data = request.data.copy()
        
        if isinstance(data, QueryDict):
            data = data.dict()  # Convert QueryDict to a regular dictionary if necessary

        # Optional: Set empty values to None
        if 'date_of_birth' in data and data['date_of_birth'] == '':
            data['date_of_birth'] = None
        if 'pincode' in data and data['pincode'] == '':
            data['pincode'] = None
        if 'image' in data and data['image'] == '':
            data['image'] = None

        if user_data:
            data['user'] = user_data

        print("Prepared data for serializer:", data)

        # Use partial=True to allow partial updates
        serializer = UserProfileSerializer(user_profile, data=data, partial=True)
        
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            print("Updated serializer data:", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            print("Serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



        
class UserDeleteView(APIView):
    def delete(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class UpdateUserStatusView(APIView):
    def patch(self, request, user_id):
        user = get_object_or_404(User, id=user_id)
        new_status = request.data.get('status')
        if new_status in ['Active', 'Inactive']:
            user.status = new_status
            user.save()
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        return Response({'status': 'error', 'message': 'Invalid status'}, status=status.HTTP_400_BAD_REQUEST)
    
from django.contrib.auth import get_user_model
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import traceback

class SaveCsvDataView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            csv_data = request.data.get('csvData', [])   

            with transaction.atomic():
                for data in csv_data:
             
                    username = data.get('username', '')  
                    email = data.get('email', '')
                    phone = data.get('phone', '')
                    first_name = data.get('first_name','')
                    last_name = data.get('last_name','')
                    password = data.get('password','')
                    date_joined = data.get('date_joined', None)  

                 
                    if email:
                        user, created = get_user_model().objects.get_or_create(
                            email=email,
                            defaults={
                                'username': username,
                                'phone': phone,
                                'first_name':first_name,
                                'last_name':last_name,
                                'password':password,
                                'is_email_verified': True,  
                                'is_phone_verified': True,
                                'otp': None,
                                'email_verification_token': None,
                                'forget_password_token': None,
                                'userrole': None
                            }
                        )
                        if not created:
                     
                            user.username = username
                            user.phone = phone
                         
                            user.save()

            return Response({'message': 'Data saved successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            traceback.print_exc()   
            return Response({'error': 'Failed to save data. Please try again.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





import random
import string
import json
import redis
from django.conf import settings


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
import json
import random

User = get_user_model()



class ForgotPasswordView(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')

        if not email:
            return Response({'error': 'Email is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Check if user with the provided email exists
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'The account does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = str(random.randint(1000, 9999))  # Generate OTP here
        cache.set(email, otp, timeout=300)  # Store OTP in cache for 5 minutes

        # Send OTP to user's email
        subject = 'Password Reset OTP'
        message = f'Your OTP for password reset is: {otp}'
        from_email = settings.EMAIL_HOST_USER
        to_email = [email]
        send_mail(subject, message, from_email, to_email)

        return Response({'status': 200, 'message': 'An OTP has been sent to your email for password reset.'}, status=status.HTTP_200_OK)
import logging

logger = logging.getLogger(__name__)
 
class VerifyForgotPasswordOtpView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = VerifyForgotPasswordOtpSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data.get('email')
            otp = serializer.validated_data.get('otp')

            cached_otp = cache.get(email)
            if not cached_otp or cached_otp != otp:
                logger.error(f"Invalid OTP for email '{email}'. Expected '{cached_otp}', received '{otp}'.")
                return Response({'status': 403, 'error': 'Invalid OTP'}, status=status.HTTP_403_FORBIDDEN)

            
            cache.delete(email)

            logger.info(f"OTP verified successfully for email '{email}'.")
            return Response({'status': 200, 'message': 'OTP verified successfully'}, status=status.HTTP_200_OK)

        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework.permissions import AllowAny
class ResetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if not email or not new_password or not confirm_password:
            return Response({'error': 'All fields are required.'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != confirm_password:
            return Response({'error': 'Passwords do not match.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            user.password = make_password(new_password)
            user.password_is_null = False
            user.save()
          
                
            return Response({'message': 'Password reset successfully.'}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        
        

class ContactMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = ContactMessageSerializer(data=request.data)
        if serializer.is_valid():
            # Optionally associate the message with the authenticated user
            serializer.validated_data['user'] = self.request.user

            try:
                # Save the contact message
                message = serializer.save()

                # Send email notification
                subject = f"New Contact Message from {message.name}"
                message_body = f"Name: {message.name}\nEmail: {message.email}\nPhone: {message.phone}\nMessage:\n{message.message}"
                recipient_email = settings.EMAIL_HOST_USER

                try:
                    send_mail(subject, message_body, settings.EMAIL_HOST_USER, [recipient_email])
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    print(f"Error sending email: {e}")
                    return Response({'status': 500, 'error': 'Failed to send email notification. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
            except Exception as e:
                print(f"Error saving contact message: {e}")
                return Response({'status': 500, 'error': 'Failed to save contact message. Please try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class EnrolledUserCountView(APIView):
    def get(self, request, slug):
        try:
            event = Event.objects.get(slug=slug)
            user_count = Enrolled.objects.filter(event=event).count()
            return Response({'user_count': user_count}, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class UserDataView(View):
    def get(self, request, *args, **kwargs):
        users = User.objects.select_related('userprofile').all()

        data = [
            {
                'id': user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_of_birth': user.userprofile.date_of_birth.strftime('%Y-%m-%d') if user.userprofile.date_of_birth else '',
                'phone': user.phone,
                'email': user.email,
                'state': user.userprofile.state if user.userprofile.state else '',
                'city': user.userprofile.city if user.userprofile.city else '',
            }
            for user in users
        ]

        return JsonResponse(data, safe=False)
    
    
    
class UserCountView(APIView):
    permission_classes = [AllowAny]  # No authentication required

    def get(self, request, format=None):
        now = timezone.now()
        seven_days_ago = now - timezone.timedelta(days=7)
        start_of_month = now.replace(day=1)

        users_last_7_days = User.objects.filter(date_joined__gte=seven_days_ago).count()
        users_this_month = User.objects.filter(date_joined__gte=start_of_month).count()

        return Response({
            'last_7_days': users_last_7_days,
            'this_month': users_this_month
        })
        
        
class ValidateEmailView(APIView):
    def get(self, request):
        email = request.GET.get('email', '')
        
        if not email:
            return Response({'status': 400, 'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'status': 200, 'exists': True}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 200, 'exists': False}, status=status.HTTP_200_OK)
        
        
        
class GeneralCheckEnrollmentView(APIView):
    def get(self, request, slug):
        if not request.user.is_authenticated:
            return Response({"enrolled": False}, status=status.HTTP_401_UNAUTHORIZED)
        
        event = get_object_or_404(GeneralEvent, slug=slug)
        user = request.user
        is_enrolled = GeneralEnrolled.objects.filter(user=user, event=event).exists()
        
        return Response({"enrolled": is_enrolled})
    
 



class GeneralEnrollEvent(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        event = get_object_or_404(GeneralEvent, slug=slug)
        user = request.user
        
        # Check if the user is already enrolled
        enrollment = GeneralEnrolled.objects.filter(user=user, event=event).first()

        if enrollment:
            # If the user is already enrolled, remove them from the enrollment
            enrollment.delete()
            
            event.is_enrolled = False
            event.save()
            
            return Response({"detail": "Successfully unenrolled from the event."}, status=status.HTTP_200_OK)
        else:
            # If the user is not enrolled, proceed to enroll them
            enrollment_data = {'user': user.id, 'event': event.id}
            serializer = GeneralEnrolledSerializer(data=enrollment_data)
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

class GeneralEnrolledUserCountView(APIView):
    def get(self, request, slug):
        try:
            event = GeneralEvent.objects.get(slug=slug)
            user_count = GeneralEnrolled.objects.filter(event=event).count()
            return Response({'user_count': user_count}, status=status.HTTP_200_OK)
        except GeneralEvent.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class GeneralFeedbackCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        print("Received data:", request.data)

        single_event_day = request.data.get('singleEvent_day')
        event_id = request.data.get('event_id')

        if not single_event_day:
            return Response({'error': 'singleEvent_day is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not event_id:
            return Response({'error': 'event_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        single_event_queryset = GeneralSingleEvent.objects.filter(day=single_event_day, event_id=event_id)
        if single_event_queryset.count() == 0:
            return Response({'error': 'SingleEvent does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        elif single_event_queryset.count() > 1:
            return Response({'error': 'Multiple SingleEvent instances found. Please provide more details to uniquely identify the event.'}, status=status.HTTP_400_BAD_REQUEST)

        single_event_instance = single_event_queryset.first()
        print("SingleEvent ID:", single_event_instance.id)

        request.data['single_event'] = single_event_instance.id

        # Check if the user has already submitted feedback for this single event
        existing_feedback = GeneralFeedback.objects.filter(user=request.user, single_event=single_event_instance).first()
        if existing_feedback:
            return Response({'error': 'You have already submitted feedback for this event.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = GeneralFeedbackSerializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            serializer.save(user=request.user, single_event=single_event_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        
        
class GeneralUserEnrolledEventListView(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_event_dates(self, event):
        # Use the correct related_name 'general_single_events'
        single_events = event.general_single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_event_times(self, event):
        # Use the correct related_name 'general_single_events'
        single_events = event.general_single_events.filter(day=1)
        if single_events.exists():
            multi_events = single_events.first().general_multi_events.all()  # Use the correct related_name
            if multi_events.exists():
                start_time = multi_events.first().starting_time
                end_time = multi_events.last().ending_time
                return start_time, end_time
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

    def get(self, request):
        user = request.user
        enrolled_events = GeneralEnrolled.objects.filter(user=user).select_related('event')

        events_data = []
        for enrollment in enrolled_events:
            event = enrollment.event
            event_status = self.get_event_status(event)
            event_data = GeneralEventListSerializer(event).data
            event_data['status'] = event_status

            start_date, end_date = self.calculate_event_dates(event)
            if start_date and end_date:
                event_data['start_date'] = start_date.strftime('%Y-%m-%d')
                event_data['end_date'] = end_date.strftime('%Y-%m-%d')
            else:
                event_data['start_date'] = "Invalid date"
                event_data['end_date'] = "Invalid date"

            if event.days == 1:
                start_time, end_time = self.calculate_event_times(event)
                if start_time and end_time:
                    event_data['start_time'] = start_time.strftime('%H:%M:%S')
                    event_data['end_time'] = end_time.strftime('%H:%M:%S')
                else:
                    event_data['start_time'] = "Invalid time"
                    event_data['end_time'] = "Invalid time"
                event_data['end_date'] = None
            else:
                event_data['start_time'] = None
                event_data['end_time'] = None

            events_data.append(event_data)

        return Response({'events': events_data})
    
    
    
class GeneralCertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        feedbacks = GeneralFeedback.objects.filter(user=user)

        if not feedbacks.exists():
            return Response({"message": "No feedback found for the user"}, status=status.HTTP_404_NOT_FOUND)

        serialized_certificates = []

        for feedback in feedbacks:
            single_event = feedback.single_event
            event = single_event.event
            certificates = GeneralCertificates.objects.filter(event=event)

            if certificates.exists():
                certificate = certificates.first()
                event_name = event.event_name
                if event.days > 1:
                    event_name += f" (Day {single_event.day})"

                serialized_certificates.append({
                    "event_name": event_name,
                    "days": event.days,
                    "event_date": single_event.date,
                    "single_event": {
                        "points": single_event.points,
                        "day": single_event.day
                    },
                    "certificate_image": certificate.image.url,
                    "feedback_created_at": feedback.created_at  # Add the feedback created at field here
                })

        return Response(serialized_certificates, status=status.HTTP_200_OK)

    
    
class GeneralEventPointsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_feedback = GeneralFeedback.objects.filter(user=request.user)
            single_events = [feedback.single_event for feedback in user_feedback]
            serializer =  GeneralSingleEventsSerializer(single_events, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GeneralUserEnrolledEventListView(APIView):
    permission_classes = [IsAuthenticated]

    def calculate_event_dates(self, event):
        """
        Calculate the start and end dates for general single events.
        """
        single_events = event.general_single_events.all()  # Corrected related name
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_event_times(self, event):
        """
        Calculate the start and end times for general multi-events when event days = 1.
        """
        single_events = event.general_single_events.filter(day=1)  # Corrected related name
        if single_events.exists():
            multi_events = single_events.first().general_multi_events.all()  # Corrected related name
            if multi_events.exists():
                start_time = multi_events.first().starting_time
                end_time = multi_events.last().ending_time
                return start_time, end_time
        return None, None

    def get_event_status(self, event):
        """
        Determine the event status (Live, Upcoming, Completed) based on current date and event times.
        """
        current_datetime = timezone.now()
        start_date, end_date = self.calculate_event_dates(event)
        start_time, end_time = self.calculate_event_times(event)

        if start_date and end_date and start_time and end_time:
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, end_time))

            if current_datetime <= event_end_datetime:
                return "Live" if current_datetime >= event_start_datetime else "Upcoming"
            else:
                return "Completed"

        return "Upcoming"

    def get(self, request):
        user = request.user
        enrolled_events = GeneralEnrolled.objects.filter(user=user).select_related('event')

        events_data = []
        for enrollment in enrolled_events:
            event = enrollment.event
            event_status = self.get_event_status(event)
            event_data = GeneralEventListSerializer(event).data
            event_data['status'] = event_status

            start_date, end_date = self.calculate_event_dates(event)
            if start_date and end_date:
                event_data['start_date'] = start_date.strftime('%Y-%m-%d')
                event_data['end_date'] = end_date.strftime('%Y-%m-%d')
            else:
                event_data['start_date'] = "Invalid date"
                event_data['end_date'] = "Invalid date"

            if event.days == 1:
                start_time, end_time = self.calculate_event_times(event)
                if start_time and end_time:
                    event_data['start_time'] = start_time.strftime('%H:%M:%S')
                    event_data['end_time'] = end_time.strftime('%H:%M:%S')
                else:
                    event_data['start_time'] = "Invalid time"
                    event_data['end_time'] = "Invalid time"
                event_data['end_date'] = None
            else:
                event_data['start_time'] = None
                event_data['end_time'] = None

            events_data.append(event_data)

        return Response({'events': events_data})

class UserCountAPIView(APIView):
    def get(self, request):
        # Adjust the query to exclude admin users
        user_count = User.objects.filter(is_staff=False, is_superuser=False).count()
        return Response({'user_count': user_count})
    
    
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.db.models.functions import TruncMonth
from django.utils.timezone import make_aware
from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()




class MonthlyUserCountAPIView(APIView):
    def get(self, request):
        # Get the current date and the start of the year
        now = datetime.now()
        start_of_year = now.replace(month=1, day=1)
        start_of_year = make_aware(start_of_year)

        # Query user counts per month, excluding superusers
        user_counts = User.objects.filter(date_joined__gte=start_of_year, is_superuser=False) \
            .annotate(month=TruncMonth('date_joined')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        # Create a dictionary with all months from March to September initialized to 0
        month_names = ['Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep']
        monthly_data = {month: 0 for month in month_names}

        # Update the monthly_data with actual counts from the query result
        for entry in user_counts:
            # Convert datetime month to its abbreviated form (e.g., 'Sep')
            month_name = entry['month'].strftime('%b')
            if month_name in monthly_data:  # Only update if within March to September
                monthly_data[month_name] = entry['count']

        # Convert the dictionary to lists for the response
        months = list(monthly_data.keys())
        counts = list(monthly_data.values())

        return Response({
            'months': months,
            'counts': counts
        })
class Last10MonthsUserCountAPIView(APIView):
    def get(self, request):
        # Get the current date
        now = datetime.now()
        # Calculate the start of the period 10 months ago
        start_of_period = now - timedelta(days=10*30)  # Approximate 10 months
        start_of_period = make_aware(start_of_period)

        # Query user counts per month for the last 10 months, excluding superusers
        user_counts = User.objects.filter(date_joined__gte=start_of_period, is_superuser=False) \
            .annotate(month=TruncMonth('date_joined')) \
            .values('month') \
            .annotate(count=Count('id')) \
            .order_by('month')

        # Create a list of months for the last 10 months including the current month
        months = [(start_of_period + timedelta(days=i*30)).strftime('%b-%Y') for i in range(9)]  # 9 months before current month
        months.append(now.strftime('%b-%Y'))  # Add current month
        monthly_data = {month: 0 for month in months}

        # Update the monthly_data with actual counts from the query result
        for entry in user_counts:
            month = entry['month'].strftime('%b-%Y')
            if month in monthly_data:  # Only update if within the last 10 months
                monthly_data[month] = entry['count']

        # Convert the dictionary to lists for the response
        months = list(monthly_data.keys())
        counts = list(monthly_data.values())

        return Response({
            'months': months,
            'counts': counts
        })
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate
class Last10DaysUserCountAPIView(APIView):
    def get(self, request):
        # Get today's date and calculate the start and end of the last 10 days
        today = datetime.now()
        start_of_period = today - timedelta(days=10)
        start_of_period = make_aware(start_of_period)

        # Query user counts per day for the last 10 days, excluding superusers
        user_counts = User.objects.filter(date_joined__gte=start_of_period, is_superuser=False) \
            .annotate(day=TruncDate('date_joined')) \
            .values('day') \
            .annotate(count=Count('id')) \
            .order_by('day')

        # Create a list of dates for the last 10 days
        days = [(start_of_period + timedelta(days=i)).strftime('%d-%b') for i in range(10)]
        daily_data = {day: 0 for day in days}

        # Update the daily_data with actual counts from the query result
        for entry in user_counts:
            day = entry['day'].strftime('%d-%b')
            if day in daily_data:  # Only update if within the last 10 days
                daily_data[day] = entry['count']

        # Convert the dictionary to lists for the response
        days = list(daily_data.keys())
        counts = list(daily_data.values())

        return Response({
            'days': days,
            'counts': counts
        })
        
class EnrolledUserView(APIView):
    def get(self, request, slug):
        print(f"Slug received: {slug}")  
        try:
            event = Event.objects.get(slug=slug)
            print(f"Event found: {event.event_name}")  
            enrolled_users = Enrolled.objects.filter(event=event).select_related('user')
            user_data = [{
                'id': user.user.id,
                'name': f"{user.user.first_name} {user.user.last_name}",
                'email': user.user.email,
                'phone': user.user.phone,
                'event_name': event.event_name
            } for user in enrolled_users]
            return Response({'enrolled_users': user_data}, status=status.HTTP_200_OK)
        except Event.DoesNotExist:
            print("Event not found")  
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


class GeneralEnrolledUserView(APIView):
    def get(self, request, slug):
        try:
            event = GeneralEvent.objects.get(slug=slug)
            enrolled_users = GeneralEnrolled.objects.filter(event=event).select_related('user')
            user_data = [{
                'id': user.user.id,
                'name': f"{user.user.first_name} {user.user.last_name}",
                'email': user.user.email,
                'phone': user.user.phone,
                'event_name': event.event_name  # Add event name here
            } for user in enrolled_users]
            return Response({'enrolled_users': user_data}, status=status.HTTP_200_OK)
        except GeneralEvent.DoesNotExist:
            return Response({'error': 'General event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class EventFeedbackListView(APIView):
    def get(self, request, single_event_id):
        try:
            single_event = SingleEvent.objects.get(id=single_event_id)
            feedbacks = Feedback.objects.filter(single_event=single_event)

            feedback_list = []
            for feedback in feedbacks:
                feedback_data = FeedbackSerializer(feedback).data
                user_data = {
                    'username': feedback.user.username,
                    'email': feedback.user.email,
                    'name': f"{feedback.user.first_name} {feedback.user.last_name}",
                    'phone': feedback.user.phone
                }
                feedback_data['user'] = user_data
                feedback_data['day'] = single_event.day  
                feedback_list.append(feedback_data)

            return Response({
                'single_event': single_event.event.event_name,
                'day': single_event.day,  # Include the day in the response
                'feedbacks': feedback_list
            })
        except SingleEvent.DoesNotExist:
            return Response({"error": "Single event not found"}, status=404)


class EventGeneralFeedbackListView(APIView):
    def get(self, request, single_event_id):
        try:
            single_event = GeneralSingleEvent.objects.get(id=single_event_id)
            feedbacks = GeneralFeedback.objects.filter(single_event=single_event)

            feedback_list = []
            for feedback in feedbacks:
                feedback_data = GeneralFeedbackSerializer(feedback).data
                user_data = {
                    'username': feedback.user.username,
                    'email': feedback.user.email,
                    'name': f"{feedback.user.first_name} {feedback.user.last_name}",
                    'phone': feedback.user.phone
                }
                feedback_data['user'] = user_data
                feedback_data['day'] = single_event.day  
                feedback_list.append(feedback_data)

            return Response({
                'single_event': single_event.event.event_name,
                'day': single_event.day,  # Include the day in the response
                'feedbacks': feedback_list
            })
        except GeneralSingleEvent.DoesNotExist:
            return Response({"error": "Single event not found"}, status=404)


class UserProfileDetailAPIView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user__id=user_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserProfiletypeSerializer(user_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, user_id, *args, **kwargs):
        try:
            user_profile = UserProfile.objects.get(user__id=user_id)
        except UserProfile.DoesNotExist:
            return Response({'error': 'User profile not found'}, status=status.HTTP_404_NOT_FOUND)

       
        userrole = request.data.get('userrole')  

       
        request_data_combined = {
            **request.data,
            'userrole': userrole   
        }

        serializer = UserProfiletypeSerializer(user_profile, data=request_data_combined, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserStatusAPIView(APIView):
    def put(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)  
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        
        new_status = request.data.get('status')

        if new_status not in ['Active', 'Inactive']:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

      
        user.status = new_status
        user.save()

    
        serializer = UserSerializer(user)   
        return Response(serializer.data, status=status.HTTP_200_OK)


 