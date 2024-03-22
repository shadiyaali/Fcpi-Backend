from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Forum)
admin.site.register(Speaker)
admin.site.register(Event)
admin.site.register(SingleEvent)
 