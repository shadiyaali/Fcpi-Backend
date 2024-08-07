from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register(Forum)
admin.site.register(Speaker)
admin.site.register(Event)
admin.site.register(SingleEvent)
admin.site.register(MultiEvent)
admin.site.register(Member)
admin.site.register(ForumMember)
admin.site.register(Blogs)
admin.site.register(BlogsContents)
admin.site.register(Certificates)
admin.site.register(Banner)
admin.site.register(News)
admin.site.register(BoardMember)
admin.site.register(Board)
admin.site.register(Gallery)
admin.site.register(GalleryImage)
admin.site.register(Attachment)
admin.site.register(UserFileAssociation)
 
 