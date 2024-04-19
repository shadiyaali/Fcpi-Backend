# users/urls.py

from django.urls import path
from .views import SecondUserCreateView,SecondUserListView,SecondUserStatusChangeView,SecondUserLoginView,SendMessageAPIView
from .views import MessageListCreateView

urlpatterns = [
    path('createuser/', SecondUserCreateView.as_view(), name='user-section-create'),
    path('second-users/', SecondUserListView.as_view(), name='second-user-list'),
    path('user/<int:pk>/', SecondUserStatusChangeView.as_view(), name='user_status_change'),
    path('login/', SecondUserLoginView.as_view(), name='second_user_login'),
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('send-message/', SendMessageAPIView.as_view(), name='send-message'),
]
