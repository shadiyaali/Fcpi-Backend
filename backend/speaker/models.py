from django.db import models

 

class SecondUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128) 
    status = models.CharField(max_length=10, choices=(('Active', 'Active'), ('Inactive', 'Inactive')), default='Active')  

    def __str__(self):
        return self.username
