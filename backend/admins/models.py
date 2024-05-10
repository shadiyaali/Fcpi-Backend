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
    
    def __str__(self):
        return self.event_name



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


    
class MultiEvent(models.Model):
    single_event = models.ForeignKey(SingleEvent, on_delete=models.CASCADE, null=True, blank=True, related_name='multi_events')
    starting_time = models.TimeField(null=True, blank=True)
    ending_time = models.TimeField(null=True, blank=True)
    topics = models.TextField(null=True, blank=True)
    single_speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE, null=True, blank=True, related_name='selected_events', default=None)

    
class Member(models.Model):     
    name = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    recent_job_title = models.CharField(max_length=100)
    additional_job_titles = models.CharField(max_length=100)
    image = models.ImageField(upload_to='members/', null=True, blank=True)
    previous_work_experience = models.CharField(max_length=100)
    publications =  models.CharField(max_length=100)
    current_research =  models.CharField(max_length=100)
    conference =  models.CharField(max_length=100)
    additional_information =  models.CharField(max_length=100)
    achievements =   models.CharField(max_length=100)
    areas =  models.CharField(max_length=100)
    
    def __str__(self):
        return self.name



class ForumMember(models.Model):    
    forum = models.ForeignKey(Forum, related_name='forum', on_delete=models.CASCADE,null=True, blank=True)
    member = models.ManyToManyField(Member, related_name='member', blank=True)


 

class Blogs(models.Model):    
    forum = models.ForeignKey(Forum, related_name='blogs', on_delete=models.CASCADE,null=True, blank=True)
    title = models.CharField(max_length=100)     
    author = models.CharField(max_length=100)
    qualification = models.CharField(max_length=100)
    date = models.DateField(null=True)
      
    def __str__(self):
        return self.title  
    
 
    
class BlogsContents(models.Model): 
    blog =  models.ForeignKey(Blogs, related_name='blog_contents', on_delete=models.CASCADE, null=True, blank=True) 
    topic = models.CharField(max_length=100,null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='blogs/', null=True, blank=True)   
    
 