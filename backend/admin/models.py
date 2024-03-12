from django.db import models

from django.contrib.auth.models import AbstractUser
 
class Admin(AbstractUser):
    is_admin = models.BooleanField(default=True)

    objects = AdminManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'
