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
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
    event_name = models.CharField(max_length=100,null=True)
    date = models.DateField(null=True)
    speakers = models.ManyToManyField(Speaker, related_name='events', blank=True)
    youtube_link = models.URLField(null=True, blank=True)
    points = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    starting_time = models.TimeField(null=True, blank=True)
    ending_time = models.TimeField(null=True, blank=True)
    topics = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return self.event_name


class Schedule(models.Model):
    event = models.ForeignKey(Event, related_name='schedules', on_delete=models.CASCADE)
    speaker = models.ForeignKey(Speaker, related_name='schedules', on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    topic = models.CharField(max_length=255, null=True)
    youtube_url = models.URLField(blank=True, null=True)
    speaker = models.ForeignKey('Speaker', related_name='assigned_schedules', on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.event.topic} - {self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%Y-%m-%d %H:%M')}"
    
