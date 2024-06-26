from django.db import models
from accounts.models import User
from admins.models import Forum,Event
from django.contrib.auth import get_user_model
 

class SecondUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    ACTIVE = 'Active'
    INACTIVE = 'Inactive'
    STATUS_CHOICES = [
        (ACTIVE, 'Active'),
        (INACTIVE, 'Inactive'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=INACTIVE)  

    def __str__(self):
        return self.username
    
 


User = get_user_model()

class Message(models.Model):
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='messages', null=True) 
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='speaker_messages')
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    answered = models.BooleanField(default=False)  # New field to track message status

    def __str__(self):
        return self.content



