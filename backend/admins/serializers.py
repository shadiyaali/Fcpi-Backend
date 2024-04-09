from rest_framework import serializers
from .models import Admin,Forum,Speaker,Event,SingleEvent,MultiEvent 

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
        fields = ['id', 'name', 'qualification', 'designation', 'description', 'photo']
      


        
class EventSpeakerSerializer(serializers.ModelSerializer):
    speakers = SpeakerSerializer(many=True)  
    class Meta:
        model = Event
        fields = ['id', 'speakers']
  

 

class MultiEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = MultiEvent
        fields = ['id', 'starting_time', 'ending_time', 'topics', 'single_speaker']

class SingleEventSerializer(serializers.ModelSerializer):
    multi_events = MultiEventSerializer(many=True, read_only=True)

    class Meta:
        model = SingleEvent
        fields = ['id', 'event', 'youtube_link', 'points', 'highlights', 'multi_events']

class EventSerializer(serializers.ModelSerializer):
    single_events = SingleEventSerializer(many=True, read_only=True)

    class Meta:
        model = Event
        fields = ['id', 'forum', 'event_name', 'speakers', 'date', 'days', 'banner', 'single_events']




class EventListSerializer(serializers.ModelSerializer):
    forum_name = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'date', 'forum', 'forum_name', 'days' ,'banner']  

    def get_forum_name(self, obj):
        return obj.forum.title if obj.forum else None