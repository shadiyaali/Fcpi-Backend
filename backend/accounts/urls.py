from django.contrib import admin
from django.urls import path, include
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view()),
    path('verifyOtp/', VerifyOtp.as_view(), name='verify_otp'),
    path('resendOtp/', ResendOtp.as_view(), name='resend-otp'),
    path('login/', LoginView.as_view(), name='login'),
    path('add_user/', AddUser.as_view(), name='add_user'),
    path('user-roles/', UserRoleListView.as_view(), name='user_roles_list'),
    path('create-roles/', UserRoleCreateView.as_view(), name='create_roles_create'),
    path('userlist/', UserListView.as_view(), name='user-list'),
    path('user-profile/', UserProfileCreateView.as_view(), name='user-profile'),
    
]
