from django.urls import path
from .views import admin_login

urlpatterns = [
    path('login/',AdminLoginView.as_view, name='admin_login'),
     
]
