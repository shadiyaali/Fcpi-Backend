from rest_framework import serializers
from .models import Admin,Forum,Speaker,Event,SingleEvent 

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ['id', 'username', 'email', 'is_admin', 'password']
        extra_kwargs = {
            'password': {'write_only': True},  
        }

    def create(self, validated_data):
        
        return Admin.objects.create_admin(**validated_data)

class ForumSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  

    class Meta:
        model = Forum
        fields = ['id','title', 'description', 'image']
        

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = '__all__'        
        
        
 

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class SingleEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleEvent
        fields = '__all__'