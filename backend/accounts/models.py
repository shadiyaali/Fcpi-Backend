from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

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

 