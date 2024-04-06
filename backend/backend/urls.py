
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static
from rest_framework.authtoken import views
from django.conf import settings
from rest_framework_simplejwt.views import (
    
    TokenObtainPairView,   
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('admins/', include('admins.urls')),
    path('speaker/', include('speaker.urls')),
 
   
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
