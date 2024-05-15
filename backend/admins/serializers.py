from rest_framework import serializers
from .models import Admin,Forum,Speaker,Event,SingleEvent,MultiEvent,Member,ForumMember,Blogs,BlogsContents,Certificates
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
        fields = ['id','forum', 'member']
        
 

class BlogsContentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogsContents
        fields = ['id', 'topic', 'description', 'image']


class BlogsSerializer(serializers.ModelSerializer):
    blog_contents = BlogsContentsSerializer(many=True, required=False)
    forum_title = serializers.CharField(source='forum.title')
    
    class Meta:
        model = Blogs
        fields = ['id', 'forum', 'title', 'author', 'qualification', 'date', 'blog_contents','forum_title']

    def create(self, validated_data):
        blog_contents_data = validated_data.pop('blog_contents', [])
        blog = Blogs.objects.create(**validated_data)

        for content_data in blog_contents_data:
            image_data = content_data.pop('image', None)
            blog_content = BlogsContents.objects.create(blog=blog, **content_data)
            if image_data:
                blog_content.image = image_data
                blog_content.save()

        return blog


class BlogsSerializerFoum(serializers.ModelSerializer):
    blog_contents = BlogsContentsSerializer(many=True, required=False)

    class Meta:
        model = Blogs
        fields = ['id', 'forum', 'title', 'author', 'qualification', 'date', 'blog_contents']

    def update(self, instance, validated_data):
        forum_data = validated_data.get('forum')
        
       
        if forum_data is None or forum_data == 'null':
            validated_data.pop('forum', None)
        
        blog_contents_data = validated_data.pop('blog_contents', None)
        
        if blog_contents_data is not None:
           
            for content_data in blog_contents_data:
                content_id = content_data.get('id')
                
                if content_id:
                    
                    try:
                        content_instance = instance.blog_contents.get(id=content_id)
                        content_serializer = BlogsContentsSerializer(instance=content_instance, data=content_data, partial=True)
                        if content_serializer.is_valid():
                            content_serializer.save()
                    except BlogsContents.DoesNotExist:
                        pass  
        
        return super().update(instance, validated_data)





class CertificatesSerializer(serializers.ModelSerializer):
        event_name = serializers.CharField(source='event.event_name', read_only=True)

        class Meta:
                model = Certificates
                fields = ['id', 'event', 'event_name', 'image']

class CertificatesListSerializer(serializers.ModelSerializer):
    event = EventSerializer()   
    class Meta:
        model = Certificates
        fields = ['id', 'event','image']
    
