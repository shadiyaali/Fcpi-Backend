# users/urls.py

from django.urls import path
from .views import *

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
    path('user/messages/<int:event_id>/', UserMessageListView.as_view(), name='message-list-by-event'),
    path('user/general_messages/<int:event_id>/', GeneralUserMessageListView.as_view(), name='message-list'),
    path('general_send-message/', GeneralSendMessageAPIView.as_view(), name='send-message'),
    path('general_messages/', GeneralMessageListView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/update/', MessageUpdateView.as_view(), name='message-update'),
    
]
 
 


 
