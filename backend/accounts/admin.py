from django.contrib import admin

 
from .models import *

admin.site.register(User)
admin.site.register(UserRole)
admin.site.register(UserProfile)