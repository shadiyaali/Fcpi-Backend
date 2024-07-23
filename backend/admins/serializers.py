from rest_framework import serializers
from .models import Admin,Forum,Speaker,Gallery,Event,GalleryImage,SingleEvent,MultiEvent,Member,ForumMember,Blogs,BlogsContents,Certificates,Banner,News,BoardMember,Board
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
        fields = ['id', 'slug', 'title', 'description', 'image']

class SpeakerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speaker
        fields = ['id', 'name', 'qualification', 'designation', 'description', 'photo']
      


        
class EventSpeakerSerializer(serializers.ModelSerializer):
    speakers = SpeakerSerializer(many=True)  
    class Meta:
        model = Event
        fields = ['id', 'slug','speakers']
  

 

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
class SingleEventSerializerss(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.CharField(required=False)  # Make optional
    youtube_link = serializers.URLField(required=False)  # Make optional
    points = serializers.DecimalField(max_digits=5, decimal_places=2, required=False)  # Make optional
    multi_events = MultiEventSerializer(many=True, required=False)  # Make optional

    class Meta:
        model = SingleEvent
        fields = ['id', 'highlights', 'youtube_link', 'points', 'multi_events']

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        single_event = SingleEvent.objects.create(**validated_data)

        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event
            MultiEvent.objects.create(**multi_event_data)

        return single_event

    def update(self, instance, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])

        instance.highlights = validated_data.get('highlights', instance.highlights)
        instance.youtube_link = validated_data.get('youtube_link', instance.youtube_link)
        instance.points = validated_data.get('points', instance.points)
        instance.save()

        # Update or create multi_events
        MultiEvent.objects.filter(single_event=instance).delete()
        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = instance
            MultiEvent.objects.create(**multi_event_data)

        return instance

class SingleEventSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    multi_events = MultiEventSerializer(many=True)

    class Meta:
        model = SingleEvent
        fields = ['id', 'highlights', 'youtube_link', 'points', 'multi_events']

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        highlights = validated_data.pop('highlights', [])

        single_event = SingleEvent.objects.create(highlights=', '.join(highlights), **validated_data)

        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event
            MultiEvent.objects.create(**multi_event_data)

        return single_event
class SingleEventGEtSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.CharField()  # Changed from ListField to CharField
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    multi_events = MultiEventSerializer(many=True)

    class Meta:
        model = SingleEvent
        fields = ['id', 'highlights', 'youtube_link', 'points', 'multi_events']

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        highlights = validated_data.pop('highlights', '')

        # If highlights is a list, concatenate it into a single string
        if isinstance(highlights, list):
            highlights = ''.join(highlights)

        # Create the SingleEvent instance with the concatenated highlights
        single_event = SingleEvent.objects.create(highlights=highlights, **validated_data)

        # Create related MultiEvent instances
        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event
            MultiEvent.objects.create(**multi_event_data)

        return single_event

from rest_framework import serializers
from .models import SingleEvent, MultiEvent

class SingleEventGetSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.CharField()  # Handle highlights as a simple CharField
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    multi_events = MultiEventSerializer(many=True)

    class Meta:
        model = SingleEvent
        fields = ['id', 'highlights', 'youtube_link', 'points', 'multi_events']

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        highlights = validated_data.pop('highlights', '')  # Expect highlights as a string

        # Create the SingleEvent instance
        single_event = SingleEvent.objects.create(highlights=highlights, **validated_data)

        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event
            MultiEvent.objects.create(**multi_event_data)

        return single_event

    def update(self, instance, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        highlights = validated_data.pop('highlights', '')  # Expect highlights as a string

        # Update the SingleEvent instance
        instance.highlights = highlights
        instance.youtube_link = validated_data.get('youtube_link', instance.youtube_link)
        instance.points = validated_data.get('points', instance.points)
        instance.save()

        # Update multi_events
        MultiEvent.objects.filter(single_event=instance).delete()
        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = instance
            MultiEvent.objects.create(**multi_event_data)

        return instance


class SingleEventUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.CharField()  # Keep as a single string
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    multi_events = MultiEventSerializer(many=True)

    class Meta:
        model = SingleEvent
        fields = ['id', 'highlights', 'youtube_link', 'points', 'multi_events']

    def create(self, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])
        single_event = SingleEvent.objects.create(**validated_data)

        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = single_event
            MultiEvent.objects.create(**multi_event_data)

        return single_event

    def update(self, instance, validated_data):
        multi_events_data = validated_data.pop('multi_events', [])

        instance.highlights = validated_data.get('highlights', instance.highlights)
        instance.youtube_link = validated_data.get('youtube_link', instance.youtube_link)
        instance.points = validated_data.get('points', instance.points)
        instance.save()

        # Update or create multi_events
        MultiEvent.objects.filter(single_event=instance).delete()
        for multi_event_data in multi_events_data:
            multi_event_data['single_event'] = instance
            MultiEvent.objects.create(**multi_event_data)

        return instance

class SingleEventlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = SingleEvent
        fields = ['id',  'points',   'date', 'day']


    

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
        fields = ['id', 'forum','slug', 'event_name', 'speakers', 'date', 'days', 'banner', 'single_events']



 
class EventListSerializer(serializers.ModelSerializer):
    forum_name = serializers.SerializerMethodField()
    single_events = SingleEventGEtSerializer(many=True, read_only=True)
    speakers = serializers.SerializerMethodField()  # Define this method to serialize speakers

    class Meta:
        model = Event
        fields = ['id', 'slug', 'event_name', 'date', 'forum', 'forum_name', 'days', 'banner', 'single_events', 'speakers']

    def get_forum_name(self, obj):
        return obj.forum.title if obj.forum else None

    def get_speakers(self, obj):
        # Assuming SpeakerSerializer is defined correctly for Speaker model
        speakers_queryset = obj.speakers.all()  # Retrieve all speakers related to this event
        return SpeakerSerializer(speakers_queryset, many=True).data  

    def get_forum_name(self, obj):
        return obj.forum.title if obj.forum else None

    
    
class EventBannerSerializer(serializers.ModelSerializer):
    banner_image = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'date', 'slug','days', 'banner_image', 'forum', 'speakers']   

    def get_banner_image(self, obj):
        if obj.banner:
            return obj.banner.url
        return None   
    
    
class MemeberSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)
    slug = serializers.SlugField(required=False)  # Slug should not be required if it's not provided in the form

    class Meta:
        model = Member
        fields = [
            'id', 'name', 'slug', 'qualification', 'recent_job_title', 'additional_job_titles',
            'image', 'previous_work_experience', 'publications', 'current_research', 'conference',
            'additional_information', 'achievements', 'areas'
        ]

        
class ForumMemberSerializer(serializers.ModelSerializer):
    member = MemeberSerializer(many=True, read_only=True)

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
        fields = ['id', 'forum', 'title', 'author', 'qualification', 'date', 'blog_contents','forum_title','blog_banner','author_profile']

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

 

 

class BlogContentsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    class Meta:
        model = BlogsContents
        fields = ['id', 'topic', 'description', 'image']

class BlogSerializer(serializers.ModelSerializer):
    blog_contents = BlogContentsSerializer(many=True, required=False)
    blog_banner = serializers.ImageField(use_url=True)
    author_profile = serializers.ImageField(use_url=True)
    forum_title = serializers.CharField(source='forum.title')

    class Meta:
        model = Blogs
        fields = ['id', 'forum','slug', 'title', 'author','forum_title', 'qualification', 'date', 'blog_contents', 'blog_banner', 'author_profile']


# serializers.py

 

class BlogsContentsSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False)

    class Meta:
        model = BlogsContents
        fields = ['id', 'topic', 'description', 'image']


class BlogsFormSerializer(serializers.ModelSerializer):
    blog_contents = BlogsContentsSerializer(many=True)

    class Meta:
        model = Blogs
        fields = ['id', 'forum', 'title', 'author', 'qualification', 'date', 'blog_banner', 'author_profile', 'blog_contents']

    def update(self, instance, validated_data):
        blog_contents_data = validated_data.pop('blog_contents', [])
        blog_contents_ids = [content['id'] for content in blog_contents_data if 'id' in content]

        # Delete any blog_contents that are not in the request
        for content in instance.blog_contents.all():
            if content.id not in blog_contents_ids:
                content.delete()

        # Update or create blog_contents
        for content_data in blog_contents_data:
            content_id = content_data.pop('id', None)
            if content_id:
                blog_content = BlogsContents.objects.get(id=content_id, blog=instance)
                for key, value in content_data.items():
                    setattr(blog_content, key, value)
                blog_content.save()
            else:
                BlogsContents.objects.create(blog=instance, **content_data)

        # Update blog instance
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()

        return instance




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
        
    
class BannerSerializer(serializers.ModelSerializer):
    banner = serializers.ImageField(required=False)  

    class Meta:
        model = Banner
        fields = ['id','url', 'banner']
    
    
class NewsSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = News
        fields = ['id','text', 'date']


 

class BoardSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Board
        fields = ['id','title' ]
        
class BoardMemberSerializer(serializers.ModelSerializer):
    member = MemeberSerializer(many=True, read_only=True)

    class Meta:
        model = BoardMember
        fields = ['id','board', 'member']
        
        
from rest_framework import serializers
 

class EventSerializer(serializers.ModelSerializer):
     
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all(), required=False)
    class Meta:
        model = Event
        fields = ('id', 'event_name', 'slug', 'speakers', 'date', 'days', 'banner', 'forum')
        
class EventSerializerupdate(serializers.ModelSerializer):
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all(), required=False)
    banner = serializers.ImageField(required=False)  

    class Meta:
        model = Event
        fields = ('id', 'event_name', 'slug', 'speakers', 'date', 'days', 'banner', 'forum')


        
class EventSerializerss(serializers.ModelSerializer):
    banner = serializers.ImageField(required=False)
     
    speakers = serializers.PrimaryKeyRelatedField(many=True, queryset=Speaker.objects.all(), required=False)
    class Meta:
        model = Event
        fields = ('id', 'event_name', 'slug', 'speakers', 'date', 'days', 'banner', 'forum')
    
    
    
class SingleEventsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    day = serializers.IntegerField() 
    event = EventSerializer()

    def create(self, validated_data):
        
        pass

    class Meta:
        model = SingleEvent
        fields = ('id', 'highlights', 'youtube_link', 'points', 'event', 'day')



class MultiSingleSerializer(serializers.ModelSerializer):
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

class SingleSingleSerializer(serializers.ModelSerializer):
    multi_events = MultiSingleSerializer(many=True, read_only=True)

    class Meta:
        model = SingleEvent
        fields = ['id', 'date', 'day', 'multi_events','youtube_link','points', 'highlights']

class EventSingleSerializer(serializers.ModelSerializer):
    single_events = SingleSingleSerializer(many=True, read_only=True)
    speakers = SpeakerSerializer(many=True)  

    class Meta:
        model = Event
        fields = ['id', 'event_name', 'date', 'days', 'forum', 'speakers', 'banner', 'single_events']


# serializers.py

 
 

class GalleryImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryImage
        fields = ('id', 'image')
class GallerySerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, required=False)

    class Meta:
        model = Gallery
        fields = ('id', 'title', 'images')

    def create(self, validated_data):
        images_data = self.context.get('request').FILES.getlist('images')

        gallery = Gallery.objects.create(title=validated_data['title'])

        for image_data in images_data:
            GalleryImage.objects.create(gallery=gallery, image=image_data)

        return gallery


from urllib.parse import unquote
import urllib.parse
  
class GalleryUpdateSerializer(serializers.ModelSerializer):
    images = GalleryImageSerializer(many=True, required=False)
    existing_images = serializers.ListField(child=serializers.CharField(), required=False, default=[])

    class Meta:
        model = Gallery
        fields = ('id', 'title', 'images', 'existing_images')

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)

        # Process existing images to keep or delete
        existing_images_urls = validated_data.get('existing_images', [])
        current_images = instance.images.all()

        # Extract IDs of existing images from URLs
        existing_image_ids = []
        for url in existing_images_urls:
            try:
                # Assuming URL format: http://127.0.0.1:8000/media/gallery/BoardofDirectors_p7xQUZ5.jpg
                image_name = unquote(url).split('/')[-1]
                image = current_images.filter(image__icontains=image_name).first()
                if image:
                    existing_image_ids.append(image.id)
            except (ValueError, IndexError, GalleryImage.DoesNotExist):
                continue

        # Delete images not in existing_image_ids
        for image in current_images:
            if image.id not in existing_image_ids:
                image.delete()

        # Process new images to add
        new_images_data = self.context['request'].FILES.getlist('images', [])
        for image_data in new_images_data:
            GalleryImage.objects.create(gallery=instance, image=image_data)

        # Save updated title
        instance.save()

        # Refresh instance to get updated relationships
        instance.refresh_from_db()

        # Return updated instance
        return instance

    def to_representation(self, instance):
        # Override to_representation to ensure correct serialization
        data = super().to_representation(instance)
        
        # Build images list with full URLs
        data['images'] = [
            {
                'id': image.id,
                'image': self.context['request'].build_absolute_uri(image.image.url)
            }
            for image in instance.images.all()
        ]
        
        # Return the modified representation
        return data

    def validate(self, data):
        if 'images' in self.context['request'].FILES or data.get('existing_images'):
            return data
        raise serializers.ValidationError("Either 'images' or 'existing_images' must be provided.")
 