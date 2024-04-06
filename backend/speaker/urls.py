# users/urls.py

from django.urls import path
from .views import SecondUserCreateView,SecondUserListView,SecondUserStatusChangeView,SecondUserLoginView

urlpatterns = [
    path('createuser/', SecondUserCreateView.as_view(), name='user-section-create'),
    path('second-users/', SecondUserListView.as_view(), name='second-user-list'),
    path('user/<int:pk>/', SecondUserStatusChangeView.as_view(), name='user_status_change'),
    path('login/', SecondUserLoginView.as_view(), name='second_user_login')
]
