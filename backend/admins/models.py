from django.db import models
from .manager import AdminManager 
from django.contrib.auth.models import AbstractUser
 
 
 
class Admin(AbstractUser):
    is_admin = models.BooleanField(default=True)
    groups = models.ManyToManyField('auth.Group', related_name='admins_admin_set')
    user_permissions = models.ManyToManyField('auth.Permission', related_name='admins_admin_set')

    objects = AdminManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
    
    
class Forum(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='forum_images/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
 

class Speaker(models.Model):
    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    designation = models.TextField()
    description = models.TextField()
    photo = models.ImageField(upload_to='speakers/', null=True, blank=True)

    def __str__(self):
        return self.name
    
from django.utils.text import slugify as django_slugify
import re   
class Event(models.Model):
    forum = models.ForeignKey(Forum, related_name='events', on_delete=models.CASCADE) 
    EVENT_TYPE_CHOICES = (
        ('Single Day', 'Single Day'),
        ('Multi Day', 'Multi Day'),  
    )
    STATUS_CHOICES = (
        ('Upcoming', 'Upcoming'),
        ('Live', 'Live'),
        ('Completed', 'Completed'),
    )
    event_name = models.CharField(max_length=100, null=True)    
    speakers = models.ManyToManyField(Speaker, related_name='events', blank=True)
    date = models.DateField(null=True) 
    days = models.IntegerField(null=True)
    banner = models.ImageField(upload_to='event_banners/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    
    def __str__(self):
        return self.event_name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.custom_slugify(self.event_name)
        super().save(*args, **kwargs)
    
    def custom_slugify(self, value):
        # Replace any character that is not alphanumeric with an underscore
        value = re.sub(r'[^\w\s]', '', value).strip().lower()
        # Replace spaces with underscores
        value = value.replace(' ', '_')
        # Remove hyphens
        value = value.replace('-', '')
        # Ensure the slug is not empty after processing
        if not value:
            value = 'default_slug'  # Provide a default slug if necessary
        return django_slugify(value)




class SingleEvent(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='single_events')          
    youtube_link = models.URLField(null=True, blank=True)
    points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)    
    highlights = models.TextField(null=True, blank=True)
    date = models.DateField(null=True) 
    day = models.IntegerField(null=True)
      
    def save(self, *args, **kwargs):
        if self._state.adding or (self.pk is not None and getattr(self, '_original_highlights', None) != self.highlights):
            if isinstance(self.highlights, list):
                self.highlights = ', '.join(self.highlights)
        super().save(*args, **kwargs)

    def refresh_from_db(self, *args, **kwargs):
        super().refresh_from_db(*args, **kwargs)
        self._original_highlights = self.highlights

    class Meta:
        unique_together = ('event', 'day')   

    def __str__(self):
        return f"{self.event.event_name}  day {self.day}"
  
    
class MultiEvent(models.Model):
    single_event = models.ForeignKey(SingleEvent, on_delete=models.CASCADE, null=True, blank=True, related_name='multi_events')
    starting_time = models.TimeField(max_length=8, null=True, blank=True)  # Change to CharField to store hh:mm
    ending_time = models.TimeField(max_length=8, null=True, blank=True)
    topics = models.TextField(null=True, blank=True)
    single_speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE, null=True, blank=True, related_name='selected_events', default=None)
   
   
    def __str__(self):
        return f"{self.single_event.event.event_name} - {self.starting_time} to {self.ending_time}"
    
import itertools 
from django.utils.text import slugify
from django.utils.crypto import get_random_string

class Member(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    qualification = models.CharField(max_length=100)
    recent_job_title = models.CharField(max_length=100)
    additional_job_titles = models.CharField(max_length=100)
    image = models.ImageField(upload_to='members/', null=True, blank=True)
    previous_work_experience = models.CharField(max_length=100)
    publications = models.CharField(max_length=100)
    current_research = models.CharField(max_length=100)
    conference = models.CharField(max_length=100)
    additional_information = models.CharField(max_length=100)
    achievements = models.CharField(max_length=100)
    areas = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = orig = slugify(self.name)
            for x in itertools.count(1):
                if not Member.objects.filter(slug=self.slug).exists():
                    break
                self.slug = '%s-%d' % (orig, x)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



class ForumMember(models.Model):    
    forum = models.ForeignKey(Forum, related_name='forum', on_delete=models.CASCADE,null=True, blank=True)
    member = models.ManyToManyField(Member, related_name='member', blank=True)

 

class Blogs(models.Model):    
    forum = models.ForeignKey(Forum, related_name='blogs', on_delete=models.CASCADE,null=True, blank=True)
    title = models.TextField( null=True, blank=True)     
    author = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    date = models.DateField(null=True)
    blog_banner = models.ImageField(upload_to='blogs_banner/', null=True, blank=True)
    author_profile = models.ImageField(upload_to='author_profile/', null=True, blank=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)  
    def __str__(self):
        return self.title  
    
 
    
class BlogsContents(models.Model): 
    blog =  models.ForeignKey(Blogs, related_name='blog_contents', on_delete=models.CASCADE, null=True, blank=True) 
    topic = models.TextField( null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)   
    
    def __str__(self):
        return f"{self.blog.title}"

class Certificates(models.Model):    
    event = models.ForeignKey(Event, related_name='certificates', on_delete=models.CASCADE,null=True, blank=True)     
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)
     
    
class Banner(models.Model):
    banner =  models.ImageField(upload_to='banner/', null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    
    
class News(models.Model):
   date = models.DateField(null=True) 
   text = models.TextField(null=True, blank=True)
   
     
 

class Board(models.Model):
    title = models.CharField(max_length=100)             
    def __str__(self):
        return self.title
    
class BoardMember(models.Model):    
    board = models.ForeignKey(Board, related_name='board', on_delete=models.CASCADE,null=True, blank=True)
    member = models.ManyToManyField(Member, related_name='board_members', blank=True)



from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = ('id', 'event_name', 'speakers', 'date', 'days', 'banner')

class SingleEventsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    highlights = serializers.ListField(child=serializers.CharField(), allow_empty=True)
    youtube_link = serializers.URLField()
    points = serializers.DecimalField(max_digits=5, decimal_places=2)
    event = EventSerializer()

    def create(self, validated_data):
        # Implementation of create method
        pass

    class Meta:
        model = SingleEvent
        fields = ('id', 'highlights', 'youtube_link', 'points', 'event')


class Gallery(models.Model):
    title = models.CharField(max_length=100)

class GalleryImage(models.Model):
    gallery = models.ForeignKey(Gallery, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.gallery.title} "