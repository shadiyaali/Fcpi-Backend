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
        
    def create(self, validated_data):
        # Get the associated SingleEvent instance from the context
        single_event = self.context['single_event']

         
        multi_event = MultiEvent.objects.create(single_event=single_event, **validated_data)
        return multi_event

 

class SingleEventSerializer(serializers.Serializer):
    highlights = serializers.ListField(child=serializers.CharField())
    youtube_link = serializers.URLField()
    points = serializers.IntegerField()
    multi_events = MultiEventSerializer(many=True)

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events')
        single_event = SingleEvent.objects.create(**validated_data)

        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event  # Add the single_event object
            MultiEvent.objects.create(**multi_event_data)

        return single_event



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