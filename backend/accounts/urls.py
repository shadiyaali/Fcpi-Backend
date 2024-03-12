from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verifyOtp/', VerifyOtp.as_view(), name='verify_otp'),
    path('resendOtp/', ResendOtp.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    
]
