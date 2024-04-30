# users/urls.py

from django.urls import path
from .views import SecondUserCreateView,SecondUserListView,SecondUserStatusChangeView,SecondUserLoginView,SendMessageAPIView,MessageListView,DeactivateUserView,MessageUpdateView,ToggleUserStatus,DeleteUser 
 

urlpatterns = [
    path('createuser/', SecondUserCreateView.as_view(), name='user-section-create'),
    path('second-users/', SecondUserListView.as_view(), name='second-user-list'),
    path('user/<int:pk>/', SecondUserStatusChangeView.as_view(), name='user_status_change'),
    path('login/', SecondUserLoginView.as_view(), name='second_user_login'),
    path('messages/', MessageListView.as_view(), name='message-list-create'),
    path('send-message/', SendMessageAPIView.as_view(), name='send-message'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    path('second-users/<int:user_id>/toggle-status/', ToggleUserStatus.as_view(), name='toggle_user_status'),
    path('second-users/<int:user_id>/', DeleteUser.as_view(), name='delete_user'),
    path('deactivate-user/<int:user_id>/', DeactivateUserView.as_view(), name='deactivate_user'),
 
]
 
 


 
