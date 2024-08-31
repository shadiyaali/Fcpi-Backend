from rest_framework import serializers
from .models import User,UserRole,UserProfile,Feedback,Enrolled,ContactMessage,GeneralEnrolled,GeneralFeedback
from admins.models import Event,Certificates,SingleEvent,GeneralSingleEvent
from admins.serializers import EventSerializer,SingleEventlistSerializer
    
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name'] 
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'password', 'phone']

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class UserAllSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'date_joined', 'last_name', 'email', 'password', 'phone']

    def create(self, validated_data):
        print(validated_data)
        user = User.objects.create(
            email=validated_data['email'],
            phone=validated_data['phone'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

 
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = ['id', 'first_name', 'last_name', 'email', 'password', 'phone']

class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = UserProfile
        fields = [
            'id', 'user', 'date_of_birth', 'image', 'primary_position', 'state',
            'primary_pharmacy_degree', 'secondary_pharmacy_degree', 'additional_degrees',
            'city', 'country', 'pharmacy_college_name', 'pharmacy_college_degree',
            'pincode', 'current_work_institution'
        ]

 
class UsersprofileSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(source='userprofile', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'phone', 'profile']
 
 

 
 

class FeedbackSerializer(serializers.ModelSerializer):
    single_event = serializers.PrimaryKeyRelatedField(queryset=SingleEvent.objects.all())

    class Meta:
        model = Feedback
        fields = [
            'id',
            'single_event',                                               
            'presentation_content',
            'speaker_delivery',
            'presentation_duration',
            'audio_video_quality',
            'how_did_you_hear',
            'suggestion',
        ]


class GeneralFeedbackSerializer(serializers.ModelSerializer):
    single_event = serializers.PrimaryKeyRelatedField(queryset=GeneralSingleEvent.objects.all())

    class Meta:
        model = GeneralFeedback
        fields = [
            'id',
            'single_event',                                               
            'presentation_content',
            'speaker_delivery',
            'presentation_duration',
            'audio_video_quality',
            'how_did_you_hear',
            'suggestion',
        ]


from admins.models import Certificates

from rest_framework.serializers import SerializerMethodField

class CertificateSerializer(serializers.ModelSerializer):
    certificate_image = SerializerMethodField()

    def get_certificate_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    class Meta:
        model = Certificates
        fields = ['id', 'event', 'certificate_image']



 
class FeedbacklistSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    event_name = serializers.CharField(source='event.name', read_only=True)
    event_date = serializers.DateField(source='event.date', read_only=True)

    class Meta:
        model = Feedback
        fields = ['id', 'user_name', 'event_name', 'event_date', 'presentation_content', 'speaker_delivery', 'presentation_duration', 'audio_video_quality', 'how_did_you_hear', 'suggestion', 'created_at']
 
 
 

class CertificatelistSerializer(serializers.ModelSerializer):
    event_name = serializers.CharField(source='event.event_name')
    event_date = serializers.DateField(source='event.date')
    single_events = serializers.SerializerMethodField()

    class Meta:
        model = Certificates
        fields = ['id', 'image', 'event_name', 'event_date', 'single_events']

    def get_single_events(self, obj):
        single_events = obj.event.single_events.all()
        if single_events.exists():
         
            sorted_single_events = single_events.order_by('day')
            
            return SingleEventlistSerializer(sorted_single_events, many=True).data
        else:
            return []


  
  
        
class UserlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name','last_name' ,'email']
        
        


class EnrolledSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrolled
        fields = ['user', 'event']

class GeneralEnrolledSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralEnrolled
        fields = ['user', 'event']
     
class EventEnrollmentCountSerializer(serializers.ModelSerializer):
    enrollment_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ('id', 'event_name', 'enrollment_count')

    def get_enrollment_count(self, obj):
        return obj.event_enrollments.count()
 
class ChangePasswordSerializer(serializers.Serializer):
   
    new_password = serializers.CharField(required=True)
    confirm_password = serializers.CharField(required=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("The new password and confirm password must match.")
        return data

class VerifyForgotPasswordOtpSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField()

    def validate(self, data):
        # No need for password-related validation here
        return data
    
    
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'message', 'created_at']