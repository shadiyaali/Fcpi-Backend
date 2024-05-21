from rest_framework import serializers
from .models import User,UserRole,UserProfile,Feedback
from admins.models import Event,Certificates,SingleEvent
from admins.serializers import EventSerializer,SingleEventlistSerializer
    
class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserRole
        fields = ['id', 'name'] 
        
        
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','first_name', 'last_name', 'email', 'password', 'phone']

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


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=False)

    class Meta:
        model = UserProfile
        fields = ['id', 'user', 'date_of_birth', 'primary_position', 'state', 'primary_pharmacy_degree', 'secondary_pharmacy_degree', 'additional_degrees', 'city', 'country', 'pharmacy_college_name', 'pharmacy_college_degree']
   
   
 
 

 
from rest_framework import serializers

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


from admins.models import Certificates

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = ['id','event', 'image']


 
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
        
        
 