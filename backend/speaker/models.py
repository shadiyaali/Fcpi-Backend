from django.db import models
from accounts.models import User

 

class SecondUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    status = models.CharField(max_length=10, choices=(('Active', 'Active'), ('Inactive', 'Inactive')), default='Active')  

    def __str__(self):
        return self.username
    
class Message(models.Model):
    content = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content