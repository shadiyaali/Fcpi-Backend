from django.urls import path
 
from .views import *

urlpatterns = [
    path('login/',SdminLogin.as_view(), name='sdmin_login'),
    
 

    
]
