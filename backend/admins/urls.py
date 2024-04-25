from django.urls import path
 
from .views import *

urlpatterns = [
    path('login/',AdminLogin.as_view(), name='admin_login'),
    path('forums/', ForumListCreate.as_view(), name='forum-list-create'),
    path('forums/<int:pk>/update/', ForumUpdateView.as_view(), name='forum-update'),
    path('forums/<int:pk>/delete/', ForumDeleteView.as_view(), name='forum-delete'),
    path('speakers/', SpeakerListCreate.as_view(), name='speaker-list-create'),
    path('speakers/<int:pk>/update/', SpeakerUpdateView.as_view(), name='speaker-update'),
    path('speakers/<int:pk>/delete/', SpeakerDeleteView.as_view(), name='speaker-delete'), 
    path('eventcreate/', EventListCreate.as_view() , name='event_create'),
    path('events/', EventListView.as_view(), name='events-list'),     
    # path('events/<int:pk>/update/', EditEventAPIView.as_view(), name='edit_event'),
    path('events/<int:pk>/list/', EventDetailView.as_view(), name='event-detail'),
    path('eventslist/', EventListView.as_view(), name='event-list'),
    path('events/<int:event_id>/single-events/', SingleEventDetailView.as_view(), name='single-events-detail'),
    path('enroll/<int:event_id>/single-events/', SingleDetailView.as_view(), name='single-events-enroll'),
    path('events/<int:event_id>/speakers/', EventSpeakersView.as_view(), name='event-speakers'),
    path('eventslistb/', EventListbannerView.as_view(), name='event-list'),

    
]
