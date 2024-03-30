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
        
        
 

 
 
class SingleEventSerializer(serializers.ModelSerializer):
    
    event = serializers.PrimaryKeyRelatedField(queryset=Event.objects.all())

    class Meta:
        model = SingleEvent
        fields = ['event', 'single_speaker', 'youtube_link', 'points', 'starting_time' 'ending_time', 'topics']




class EventSerializer(serializers.ModelSerializer):
  
    speakers = serializers.StringRelatedField(many=True)  

    
    single_events = SingleEventSerializer(many=True, read_only=True)
    banner = serializers.ImageField(required=False)   

    class Meta:
        model = Event
        fields = ['id', 'days', 'forum', 'event_name', 'date', 'speakers', 'banner', 'single_events', 'highlights']




class EventListSerializer(serializers.ModelSerializer):
    forum_name = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'date', 'forum', 'forum_name', 'days' ,'banner']  

    def get_forum_name(self, obj):
        return obj.forum.title if obj.forum else None