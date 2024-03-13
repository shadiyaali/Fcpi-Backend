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
    # slug = AutoSlugField(populate_from='title', null=True)