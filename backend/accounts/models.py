from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager
from django.utils import timezone

class UserRole(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=12)
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    otp = models.CharField(max_length=4, null=True, blank=True)
    email_verification_token = models.CharField(max_length=200, null=True, blank=True)
    forget_password_token = models.CharField(max_length=200, null=True, blank=True)
    userrole = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)


    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone']   

    objects = UserManager()   

    def name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.email

class UserProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    primary_position = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    primary_pharmacy_degree = models.CharField(max_length=100, null=True, blank=True)
    secondary_pharmacy_degree = models.CharField(max_length=100, null=True, blank=True)
    additional_degrees = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    pharmacy_college_name = models.CharField(max_length=100, null=True, blank=True)
    pharmacy_college_degree = models.CharField(max_length=100, null=True, blank=True)

 

    def __str__(self):
        return self.user.email
 
 

 

class Feedback(models.Model):
    user = models.ForeignKey(User, related_name='feedback', on_delete=models.CASCADE,blank= True,default=True) 
    SATISFACTION_CHOICES = [
        ('VS', 'Very Satisfied'),
        ('SS', 'Somewhat Satisfied'),
        ('N', 'Neutral'),
        ('US', 'Unsatisfied'),
        ('VU', 'Very Unsatisfied'),
    ]
    
    HEAR_CHOICES = [
       ('E', 'Email'),
       ('S', 'Social Media Post'),
       ('W', 'WhatsApp'),
       ('F', 'FCPI Website'),
       ('R', 'Referral'),
       ('I', 'IDCongress2023'),
       ('O', 'Other'),
    ]

    presentation_content = models.CharField(max_length=2, choices=SATISFACTION_CHOICES, null=True)
    speaker_delivery = models.CharField(max_length=2, choices=SATISFACTION_CHOICES, null=True)
    presentation_duration = models.CharField(max_length=2, choices=SATISFACTION_CHOICES, null=True)
    audio_video_quality = models.CharField(max_length=2, choices=SATISFACTION_CHOICES, null=True)
    how_did_you_hear = models.CharField(max_length=1, choices=HEAR_CHOICES, null=True)
    suggestion = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now, null=True)

    def __str__(self):
        return f"Feedback - {self.created_at}"






    