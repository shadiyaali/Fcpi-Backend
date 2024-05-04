from rest_framework import serializers
from .models import Admin,Forum,Speaker,Event,SingleEvent,MultiEvent,Member,ForumMember
from datetime import datetime
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
    speaker_name = serializers.SerializerMethodField()

    class Meta:
        model = MultiEvent
        fields = ['id', 'starting_time', 'ending_time', 'topics', 'single_speaker', 'speaker_name']

    def create(self, validated_data):
        single_event = self.context['single_event']
        multi_event = MultiEvent.objects.create(single_event=single_event, **validated_data)
        return multi_event

    def get_speaker_name(self, obj):
        return obj.single_speaker.name if obj.single_speaker else None

    

class SingleEventSerializer(serializers.Serializer):
    highlights = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    multi_events = MultiEventSerializer(many=True)

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        highlights = validated_data.pop('highlights', [])

        single_event = SingleEvent.objects.create(highlights=', '.join(highlights), **validated_data)

        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event
            MultiEvent.objects.create(**multi_event_data)

        return single_event



class RetrieveSingleEventSerializer(serializers.Serializer):
    highlights = serializers.CharField()
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    multi_events = MultiEventSerializer(many=True)

    def to_representation(self, instance):
        return {
            'highlights': instance.highlights.split(', '),
            'youtube_link': instance.youtube_link,
            'points': instance.points,
            'multi_events': MultiEventSerializer(instance.multi_events, many=True).data
        }

 
 

class EventSerializer(serializers.ModelSerializer):
    single_events = SingleEventSerializer(many=True, read_only=True)
    date = serializers.DateField(format='%Y-%m-%d')   

    class Meta:
        model = Event
        fields = ['id', 'forum', 'event_name', 'speakers', 'date', 'days', 'banner', 'single_events']



 
class EventListSerializer(serializers.ModelSerializer):
    forum_name = serializers.SerializerMethodField()
    single_events = SingleEventSerializer(many=True, read_only=True)
     

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'date', 'forum', 'forum_name', 'days', 'banner', 'single_events' ]

    def get_forum_name(self, obj):
        return obj.forum.title if obj.forum else None

     
    
class EventBannerSerializer(serializers.ModelSerializer):
    banner_image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'date', 'days', 'banner_image', 'forum', 'speakers']   

    def get_banner_image(self, obj):
        if obj.banner:
            return obj.banner.url
        return None   
    
    
class MemeberSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)  

    class Meta:
        model = Member
        fields = ['id','name', 'qualification', 'recent_job_title','additional_job_titles','image','previous_work_experience','publications','current_research','conference','additional_information','achievements','areas']
        
        
class ForumMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForumMember
        fields = ['forum', 'member']