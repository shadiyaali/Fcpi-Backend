from rest_framework import serializers
from .models import User,UserRole,UserProfile,Feedback
from admins.models import Event,Certificates
    
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
   
   
 
 

class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['presentation_content' , 'speaker_delivery', 'presentation_duration', 'audio_video_quality', 'how_did_you_hear', 'suggestion']



class CertificategenerateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificates
        fields = ['image']


 