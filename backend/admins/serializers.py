from rest_framework import serializers
from .models import Admin,Forum,Speaker,Event,EventSpeaker 

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

class EventSpeakerSerializer(serializers.ModelSerializer):
    event = EventSerializer()  # Nested serializer for Event

    class Meta:
        model = EventSpeaker
        fields = '__all__'

    def create(self, validated_data):
        event_data = validated_data.pop('event')  # Extract event data
        event_serializer = EventSerializer(data=event_data)
        if event_serializer.is_valid():
            event = event_serializer.save()  # Save the event object
            event_speaker = EventSpeaker.objects.create(event=event, **validated_data)  # Create EventSpeaker
            return event_speaker
        else:
            raise serializers.ValidationError("Error in event data")