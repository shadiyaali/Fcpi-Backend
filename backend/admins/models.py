from django.db import models
from .manager import AdminManager 
from autoslug import AutoSlugField
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
    
    
   
    
          
    def __str__(self):
        return self.title

 

class Speaker(models.Model):
    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    description = models.TextField()
    photo = models.ImageField(upload_to='speakers/', null=True, blank=True)

    def __str__(self):
        return self.name
    
    
class Event(models.Model):
    forum = models.ForeignKey(Forum, related_name='events', on_delete=models.CASCADE) 
    EVENT_TYPE_CHOICES = (
        ('Single Day', 'Single Day'),
        ('Multi Day', 'Multi Day'),
    )
 
    event_name = models.CharField(max_length=100, null=True)
    date = models.DateField(null=True)
    speakers = models.ManyToManyField(Speaker, related_name='events', blank=True)
    single_speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE, null=True, blank=True, related_name='selected_events', default=None)
    youtube_link = models.URLField(null=True, blank=True)
    points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    starting_time = models.TimeField(null=True, blank=True)
    ending_time = models.TimeField(null=True, blank=True)
    topics = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.event_name

class EventSpeaker(models.Model):
    days = models.ImageField()
    events = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='events') 
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE, null=True, blank=True, related_name='speakers' )
    date = models.DateField(null=True)
    
    

   

    
