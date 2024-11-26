from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminSerializer,ForumSerializer,GeneralMultiEventSerializer,PodcastUpdateSerializer,MultiEventupppSerializer,SingleEventupppSerializer, SingleEventuppSerializer, MultiEventuppSerializer,PodcastSerializer ,NewsletterSerializer,GeneralCertificatesSerializer,GeneralAttachmentSerializer,GeneralEventBannerSerializer,GeneralEventSpeakerSerializer,GeneralRetrieveSingleEventSerializer, GeneralSingleAllEventSerializer,GeneralEventListSerializer,GeneralEventSerializer,GeneralSingleEventSerializer, GalleryUpdateSerializer,MemeberAddSerializer,GeneralBlogSerializer,BlogsGeneralFormSerializer, AttachmentSerializerss,GeneralBlogsSerializer,SingleAllEventSerializer,AttachmentSerializer,EventSerializerss,SingleEventSerializerss,GallerySerializer,BlogSerializer,GalleryImageSerializer,BoardSerializer,SpeakerSerializer,BoardMemberSerializer,EventSingleSerializer,CertificatesListSerializer,BannerSerializer,NewsSerializer,BlogsFormSerializer,EventSerializer,CertificatesSerializer,BlogsSerializer,BlogsContentsSerializer,SingleEventSerializer,ForumMemberSerializer,MemeberSerializer,EventListSerializer,EventSpeakerSerializer,MultiEventSerializer,RetrieveSingleEventSerializer,EventBannerSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from.models import Forum,Speaker,Event,SingleEvent,Gallery,Admin,GeneralAttachment,Podcastfcpipodcast ,GeneralEvent,GeneralUserFileAssociation,Newsletter,GeneralCertificates,GeneralSingleEvent,GeneralMultiEvent,Attachment,GeneralBlogsContents,GeneralBlogs,UserFileAssociation,MultiEvent,Member,ForumMember,BlogsContents,Blogs,Certificates,Banner,News,BoardMember,Board
from datetime import datetime, timedelta
from rest_framework.exceptions import APIException 
from rest_framework.exceptions import NotFound
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
import json 
import logging 
from rest_framework.generics import UpdateAPIView 
from rest_framework_simplejwt.tokens import RefreshToken

class AdminLogin(APIView):
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        
        if email is None or password is None:
            return Response({'error': 'Email and password must be provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.is_staff and user.is_superuser:
            refresh = RefreshToken.for_user(user)
            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        
        return Response({'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)


 
from django.views import View
class CheckAuthView(View):
   
    def get(self, request, *args, **kwargs):
        if request.user.is_staff and request.user.is_superuser:
            return JsonResponse({'isAuthenticated': True})
        return JsonResponse({'isAuthenticated': False})
from django.contrib.auth import logout
class AdminLogout(APIView):
    def post(self, request):
        try:
            logout(request)
            return Response({'status': 200, 'message': 'Logged out successfully'})
        except Exception as e:
            print("An error occurred:", e)
            return Response({'status': 500, 'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 

class ForumListCreate(generics.ListCreateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

class ForumUpdateView(generics.UpdateAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

class ForumDeleteView(generics.DestroyAPIView):
    queryset = Forum.objects.all()
    serializer_class = ForumSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class SpeakerListCreate(generics.ListCreateAPIView):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

    def perform_create(self, serializer):
        serializer.save()

class SpeakerRetrieve(generics.RetrieveAPIView):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

class SpeakerUpdateView(generics.UpdateAPIView):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    

class SpeakerDeleteView(generics.DestroyAPIView):
    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
  




 
 
logger = logging.getLogger(__name__) 

# Adjusting EventListCreate view
class EventListCreate(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            print("Request Data:", request.data)

            speakers_list = request.data.getlist('speakers')   
            print("Extracted Speakers List:", speakers_list)

            event_data = {
                'event_name': request.data.get('event_name'),
                'date': None,
                'days': int(request.data.get('days', 1)),
                'forum': request.data.get('forum'),
                'speakers': speakers_list,
                'banner': request.data.get('banner')
            }

            date_str = request.data.get('date')
            if date_str:
                try:
                    event_data['date'] = datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                except ValueError:
                    return Response({'error': 'Invalid date format. Use DD-MM-YYYY.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date = datetime.strptime(event_data['date'], '%Y-%m-%d') if event_data['date'] else None
            dates = [start_date + timedelta(days=i) for i in range(event_data['days'])] if start_date else []

            print("Event Data before serialization:", event_data)

            forum_id = event_data.get('forum')
            if not Forum.objects.filter(id=forum_id).exists():
                return Response({'error': 'Invalid forum ID'}, status=status.HTTP_400_BAD_REQUEST)

            event_serializer = EventSerializer(data=event_data)
            if event_serializer.is_valid():
                print("Event Serializer:", event_serializer)
                event = event_serializer.save()

                single_events_data = request.data.getlist('single_events[]')
                print("Single Events Data:", single_events_data)

                for date_index, date in enumerate(dates):
                    single_event_data_dict = json.loads(single_events_data[date_index])
                    single_event_data_dict['date'] = date.strftime('%Y-%m-%d')
                    single_event_data_dict['day'] = date_index + 1
                    single_serializer = SingleEventSerializer(data=single_event_data_dict)
                    if single_serializer.is_valid():
                        single_instance = single_serializer.save(event=event, date=date, day=date_index + 1)

                        multi_events_data = single_serializer.validated_data.get('multi_events', [])
                        for multi_event_data in multi_events_data:
                            existing_multi_event = MultiEvent.objects.filter(
                                single_event=single_instance,
                                starting_time=multi_event_data['starting_time'],
                                ending_time=multi_event_data['ending_time']
                            ).first()

                            if not existing_multi_event:
                                multi_event_data['single_event'] = single_instance.id
                                multi_serializer = MultiEventSerializer(data=multi_event_data, context={'single_event': single_instance})
                                if multi_serializer.is_valid():
                                    multi_serializer.save()
                                else:
                                    print("Multi Event Serializer Errors:", multi_serializer.errors)
                                    return Response(multi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print("Single Event Serializer Errors:", single_serializer.errors)
                        return Response(single_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({'message': 'Event and associated data created successfully'}, status=status.HTTP_201_CREATED)

            else:
                print("Event Serializer Errors:", event_serializer.errors)
                return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Adjusting EventSerializer
 



class EventListSingleView(APIView):
    def get(self, request, pk):   
        try:
            event = Event.objects.get(id=pk)   
            serializer = EventSingleSerializer(event)   
            return Response(serializer.data)
        except Event.DoesNotExist:  
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:   
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    
class EventListAllView(APIView):
    def get(self, request):
       
        events = Event.objects.all()
        serializer = EventListSerializer(events, many=True)
        print("serializer.data forum",serializer.data)
        return Response(serializer.data)
    
class GeneralSingleEventListAllView(APIView):
    def get(self, request):
        single_events = GeneralSingleEvent.objects.all()
        serializer = GeneralSingleAllEventSerializer(single_events, many=True)
        print("serializer.data",serializer.data)
        return Response(serializer.data)   
 
 
 


 

 

# views.py
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from django.db import transaction
import json
from datetime import timedelta

from .models import Event, SingleEvent, MultiEvent, Forum
from .serializers import EventSerializer

class EventUpdateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Ensure to include parsers for handling file uploads

    @transaction.atomic
    def put(self, request, event_id):
        try:
            print("Request Data:", request.data)
            print("Request Files:", request.FILES)  # Debug: Print files in request

            # Fetch the event to update
            event = get_object_or_404(Event, id=event_id)
            speakers_list = request.data.getlist('speakers')
            print("Extracted Speakers List:", speakers_list)

            speakers_list = [int(speaker_id) for speaker_id in speakers_list]

            # Prepare data for updating the event
            event_name = request.data.get('event_name')
            date_str = request.data.get('date')
            days = int(request.data.get('days', 1))
            forum_id = request.data.get('forum')
            
            # Handle file upload for banner
            if 'banner' in request.FILES:
                event.banner = request.FILES['banner']  # Use request.FILES to get the uploaded file

            # Validate and parse the date
            if date_str:
                try:
                    event_date = parse_date(date_str)
                    if not event_date:
                        raise ValueError("Invalid date format.")
                except ValueError:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                event_date = None

            if not Forum.objects.filter(id=forum_id).exists():
                return Response({'error': 'Invalid forum ID'}, status=status.HTTP_400_BAD_REQUEST)

            # Update event fields
            event.event_name = event_name
            event.date = event_date
            event.days = days
            event.forum_id = forum_id
            event.save()  # Save the updated event before updating related data
            
            # Update the speakers associated with the event
            event.speakers.set(speakers_list)

            # **Key Change**: Don't delete all SingleEvents, update or create new ones
            single_events_data = json.loads(request.data.get('single_events', '[]'))
            print("Single Events Data:", single_events_data)

            # Create dates for the single events
            dates = [event_date + timedelta(days=i) for i in range(days)] if event_date else []
            if len(single_events_data) < len(dates):
                return Response({'error': 'Insufficient single events data.'}, status=status.HTTP_400_BAD_REQUEST)

            # Loop through the dates and single events
            for date_index, date in enumerate(dates):
                single_event_data = single_events_data[date_index]

                # Update or create SingleEvent based on event and day
                single_event, created = SingleEvent.objects.update_or_create(
                    event=event,
                    day=date_index + 1,
                    defaults={
                        'date': date.strftime('%Y-%m-%d'),
                        'youtube_link': single_event_data.get('youtube_link'),
                        'points': single_event_data.get('points'),
                        'highlights': single_event_data.get('highlights', []),
                    }
                )

                # Handle MultiEvent for each SingleEvent
                MultiEvent.objects.filter(single_event=single_event).delete()  # You may want to handle this more carefully
                for multi_event_data in single_event_data.get('multi_events', []):
                    single_speaker_id = multi_event_data.get('single_speaker')
                    if isinstance(single_speaker_id, dict):
                        single_speaker_id = single_speaker_id.get('id')
                    
                    MultiEvent.objects.create(
                        single_event=single_event,
                        starting_time=multi_event_data.get('starting_time'),
                        ending_time=multi_event_data.get('ending_time'),
                        topics=multi_event_data.get('topics'),
                        single_speaker_id=single_speaker_id,
                    )

            return Response({'message': 'Event and associated data updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)










        
class EventDetailView(APIView):
    def get(self, request, pk):
        try:
            event = Event.objects.prefetch_related('single_events').get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            print('error')
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
            
 

 


from datetime import datetime, timedelta

 
 

from django.utils import timezone
from datetime import datetime, timedelta

class EventListView(APIView):
    def calculate_event_times(self, event):
        """
        Calculates the start date, end date, earliest start time, and latest end time
        for an event based on its single and multi events.
        """
        single_events = event.single_events.all()

        if not single_events.exists():
            return None, None, None, None

      
        start_date = single_events.first().date
        end_date = single_events.last().date

        earliest_start_time = None
        latest_end_time = None

        
        for single_event in single_events:
            multi_events = single_event.multi_events.all()

            for multi_event in multi_events:
                # Find the earliest starting time
                if earliest_start_time is None or multi_event.starting_time < earliest_start_time:
                    earliest_start_time = multi_event.starting_time
                
                # Find the latest ending time
                if latest_end_time is None or multi_event.ending_time > latest_end_time:
                    latest_end_time = multi_event.ending_time

        return start_date, end_date, earliest_start_time, latest_end_time

    def calculate_last_single_event_end_time(self, event):
        """
        Calculates the ending time of the last multi-event in the last single event.
        """
        single_events = event.single_events.all()

        if not single_events.exists():
            return None

        # Get the last single event
        last_single_event = single_events.last()

        # Get the last multi-event in the last single event
        last_multi_event = last_single_event.multi_events.last()

        # Return the ending time of the last multi-event if it exists
        if last_multi_event:
            return last_multi_event.ending_time
        return None

    def get_event_status(self, event):
        """
        Determines the status of the event based on the current datetime and the last multi-event's
        ending time in the last single event.
        """
        current_datetime = timezone.now()
        start_date, end_date, start_time, _ = self.calculate_event_times(event)

        # Get the ending time of the last multi-event in the last single event
        last_multi_event_end_time = self.calculate_last_single_event_end_time(event)

        if start_date and end_date and start_time and last_multi_event_end_time:
            # Make the event start datetime timezone-aware
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))

            # Use the end date and the ending time of the last multi-event for event completion
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, last_multi_event_end_time))

            # Add 15-minute buffers for live status
            live_start_datetime = event_start_datetime - timedelta(minutes=15)
            live_end_datetime = event_end_datetime + timedelta(minutes=15)

            print(f"Current Time: {current_datetime}")
            print(f"Event Start Time: {event_start_datetime}")
            print(f"Event End Time (based on last multi-event): {event_end_datetime}")
            print(f"Fifteen Minutes Before Start: {live_start_datetime}")
            print(f"Fifteen Minutes After End: {live_end_datetime}")

            # Determine the event status
            if current_datetime < live_start_datetime:
                return "Upcoming"   
            elif live_start_datetime <= current_datetime <= live_end_datetime:
                return "Live"   
            elif current_datetime > live_end_datetime:
                return "Completed"

        return "Upcoming"  # Default to upcoming if dates are missing

    def get(self, request):
        """
        Retrieves all events, categorizes them based on status, and returns serialized data.
        """
        events = Event.objects.all()
        live_events_data = []
        upcoming_events_data = []
        completed_events_data = []

        for event in events:
            # Calculate event status
            status = self.get_event_status(event)

            # Calculate event dates and times
            start_date, end_date, start_time, end_time = self.calculate_event_times(event)

            # Serialize event data and add start/end times
            event_data = EventListSerializer(event).data
            event_data['start_date'] = start_date
            event_data['end_date'] = end_date
            event_data['times'] = {
                'start_time': start_time,
                'end_time': end_time
            }

            # Categorize events based on their status
            if status == "Live":
                live_events_data.append(event_data)
            elif status == "Upcoming":
                upcoming_events_data.append(event_data)
            else:
                completed_events_data.append(event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })

 
 


from datetime import datetime

class SingleEventDetailView(APIView):
    def get(self, request, slug):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events__multi_events'), slug=slug)
            serialized_data = EventListSerializer(event, context={'request': request}).data
            serialized_single_events = []
            single_events = event.single_events.all().order_by('day')

            for single_event in single_events:
                single_event_dict = RetrieveSingleEventSerializer(single_event).data
                single_event_dict['day'] = single_event.day

                multi_events = single_event.multi_events.all().order_by('starting_time')

                if multi_events.exists():
                    first_multi_event = multi_events.first()
                    last_multi_event = multi_events.last()

                    # Assign start and end times directly from MultiEvent
                    if first_multi_event.starting_time:
                        single_event_dict['first_multi_event_start'] = str(first_multi_event.starting_time)
                    if last_multi_event.ending_time:
                        single_event_dict['last_multi_event_end'] = str(last_multi_event.ending_time)

                serialized_single_events.append(single_event_dict)
                print("serialized_single_events",serialized_single_events)

            if single_events.exists():
                serialized_data['start_date'] = single_events.first().date.strftime('%Y-%m-%d')
                serialized_data['end_date'] = single_events.last().date.strftime('%Y-%m-%d')
            else:
                serialized_data['start_date'] = None
                serialized_data['end_date'] = None

            serialized_data['single_events'] = serialized_single_events

            return Response(serialized_data)

        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)


 

from django.utils import timezone

class SingleDetailView(APIView):
    def get(self, request, slug):
        try:
            # Fetch the event with related data
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events__multi_events'), slug=slug)
            serialized_data = EventListSerializer(event, context={'request': request}).data

            serialized_single_events = []
            current_date = timezone.now().date()  # Get the current date

            # Sort single_events by date
            sorted_single_events = sorted(event.single_events.all(), key=lambda se: se.date)

            # Initialize start_date and end_date
            start_date = None
            end_date = None

            for index, single_event in enumerate(sorted_single_events, start=1):
                serialized_single_event = SingleEventSerializer(single_event).data
                serialized_single_event['day'] = index  
                serialized_single_event['date'] = single_event.date.strftime('%Y-%m-%d')
                
                # Check if the event is live or completed
                serialized_single_event['is_live_or_completed'] = single_event.date <= current_date
                
                # Handle multi-events within the single event
                multi_events = single_event.multi_events.all().order_by('starting_time')
                if multi_events.exists():
                    first_multi_event = multi_events.first()
                    last_multi_event = multi_events.last()

                    # Assign start and end times directly from MultiEvent
                    serialized_single_event['first_multi_event_start'] = str(first_multi_event.starting_time) if first_multi_event.starting_time else None
                    serialized_single_event['last_multi_event_end'] = str(last_multi_event.ending_time) if last_multi_event.ending_time else None
                
                serialized_single_events.append(serialized_single_event)

            # Set start_date and end_date based on the earliest and latest single events
            if sorted_single_events:
                start_date = sorted_single_events[0].date.strftime('%Y-%m-%d')
                end_date = sorted_single_events[-1].date.strftime('%Y-%m-%d')

            serialized_data['start_date'] = start_date
            serialized_data['end_date'] = end_date
            serialized_data['single_events'] = serialized_single_events

            return Response(serialized_data)
               
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
     
            
class EventSpeakersView(APIView):
    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        serializer = EventSpeakerSerializer(event)
       
        return Response(serializer.data)

from django.utils import timezone
from datetime import datetime, timedelta

class EventListbannerView(APIView):
    def calculate_end_date(self, event):
        """
        Calculates the start and end dates of the event based on its single events.
        """
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_multi_event_times(self, event):
        """
        Calculates the starting time of the first MultiEvent and ending time of the last MultiEvent
        when days = 1 for the given event.
        """
        single_event = event.single_events.filter(day=1).first()
        if single_event:
            multi_events = single_event.multi_events.all()
            if multi_events.exists():
                start_time = multi_events.first().starting_time
                end_time = multi_events.last().ending_time
                return start_time, end_time
        return None, None

    def get_event_status(self, event):
        """
        Determines the status of the event based on current datetime and multi-event times,
        with a 15-minute buffer for live status.
        """
        current_datetime = timezone.now()  # Get the current time
        start_date, end_date = self.calculate_end_date(event)
        start_time, end_time = self.calculate_multi_event_times(event)

        if start_date and end_date and start_time and end_time:
            # Combine date and time to get the full datetime for start and end
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, end_time))

            # Adding the 15-minute buffer before the start and after the end
            live_start_datetime = event_start_datetime - timedelta(minutes=15)
            live_end_datetime = event_end_datetime + timedelta(minutes=15)

            # Determine event status based on the current time and the time buffers
            if current_datetime < live_start_datetime:
                return "Upcoming"  # Before 15 minutes of the first multi-event's start time
            elif live_start_datetime <= current_datetime <= live_end_datetime:
                return "Live"  # Within the 15 minutes before start and 15 minutes after the last end time
            elif current_datetime > live_end_datetime:
                return "Completed"  # After 15 minutes of the last multi-event's end time
        return "Upcoming"

    def get(self, request):
        """
        Retrieves all events, categorizes them based on status, and returns serialized data.
        """
        events = Event.objects.all()
        live_events_data = []
        upcoming_events_data = []
        completed_events_data = []

        for event in events:
            # Determine event status
            status = self.get_event_status(event)

            # Calculate start and end dates
            start_date, end_date = self.calculate_end_date(event)

            # Calculate start and end times of MultiEvent for days = 1
            start_time, end_time = self.calculate_multi_event_times(event)

            # Serialize event data
            event_data = EventBannerSerializer(event).data
            event_data['start_date'] = start_date
            event_data['end_date'] = end_date
            event_data['times'] = {
                'start_time': start_time,
                'end_time': end_time
            }

            # Append to appropriate list based on status
            if status == "Live":
                live_events_data.append(event_data)
            elif status == "Upcoming":
                upcoming_events_data.append(event_data)
            else:
                completed_events_data.append(event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })



class MemberListCreate(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemeberAddSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()


class MemberUpdateView(generics.UpdateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemeberSerializer
    parser_classes = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        print("Request Data:", request.data)  # Log incoming data
        
        try:
            # Call the superclass's update method
            response = super().update(request, *args, **kwargs)
            
            # Fetch and serialize the updated instance
            instance = self.get_object()
            serializer = self.get_serializer(instance)
            print("Updated Data:", serializer.data)  # Log updated data
            
            return response
        except Exception as e:
            print(f"Error during update: {str(e)}")  # Log any errors
            raise

class MemberDeleteView(generics.DestroyAPIView):
    queryset = Member.objects.all()
    serializer_class = MemeberSerializer
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
class ForumMemberCreateView(generics.CreateAPIView):
    serializer_class = ForumMemberSerializer

    def create(self, request, *args, **kwargs):
        forum_id = request.data.get('forum')
        selected_members = request.data.get('members', [])

        
        existing_forum_member = ForumMember.objects.filter(forum_id=forum_id).first()
        if existing_forum_member:
            return Response({"error": "Forum member already exists for this forum."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        forum_member_instance = serializer.save()
        forum_member_instance.member.add(*selected_members)

        return Response({"message": "Forum member created successfully."}, status=status.HTTP_201_CREATED)





class ForumMemberListView(APIView):
    def get(self, request, forum_id):
        try:           
            forum_members = ForumMember.objects.filter(forum=forum_id)            
            serializer = ForumMemberSerializer(forum_members, many=True)
       
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
 
 
class ForumExcludeView(APIView):
    def get(self, request, forum_id):
        try:
            all_members = Member.objects.all()
            forum_members = ForumMember.objects.filter(forum=forum_id).values_list('member_id', flat=True)
            members_not_in_forum = all_members.exclude(id__in=forum_members)
            serializer = MemeberSerializer(members_not_in_forum, many=True)
            print("serializer",serializer.data)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
class ForumMemberView(APIView):
    def put(self, request, forum_id, format=None):
        print("request",request.data)
        try:
            forum_member = ForumMember.objects.get(forum_id=forum_id)
        except ForumMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        selected_members = request.data.get('members', [])
        deleted_members = request.data.get('deleted_members', [])
        print("kkkkk", selected_members)
        print("DDDDD", deleted_members)
        
    
        if selected_members:
            forum_member.member.add(*selected_members)

    
        if deleted_members:
            forum_member.member.remove(*deleted_members)

      
        for member_id in deleted_members:
            if member_id in selected_members:
                forum_member.member.add(member_id)

        serializer = ForumMemberSerializer(forum_member)
        print("ssssss", serializer.data)
        return Response(serializer.data)




 
 
from django.http import QueryDict

class CreateBlog(APIView):
    def post(self, request):
        try:
            print("Request data:", request.data)
            with transaction.atomic():
             
                forum_id = request.data.get('forum')
                title = request.data.get('title')
                author = request.data.get('author')
                qualification = request.data.get('qualification')
                date = request.data.get('date')
                blog_banner = request.data.get('blog_banner')
                author_profile = request.data.get('author_profile')
                
             
                blog = Blogs.objects.create(
                    forum_id=forum_id,
                    title=title,
                    author=author,
                    qualification=qualification,
                    date=date,
                    blog_banner=blog_banner,
                    author_profile=author_profile
                )
                
               
                blog_contents = []
                for key in request.data.keys():
                    if key.startswith('blog_contents'):
                        index = key.split('[')[1].split(']')[0]
                        if len(blog_contents) <= int(index):
                            blog_contents.append({})
                        field = key.split('[')[2].split(']')[0]
                        blog_contents[int(index)][field] = request.data.get(key)
                
                print("Extracted blog contents:", blog_contents)

                for content_data in blog_contents:
                    topic = content_data.get('topic')
                    description = content_data.get('description')
                    image = request.data.get(f'blog_contents[{blog_contents.index(content_data)}][image]')
                    
                    content = BlogsContents.objects.create(
                        blog=blog,
                        topic=topic,
                        description=description,
                        image=image
                    )
                        
        except Exception as e:
            print("Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_201_CREATED)



class CreateGeneralBlog(APIView):
    def post(self, request):
        try:
            print("Request data:", request.data)
            with transaction.atomic():
                title = request.data.get('title')
                author = request.data.get('author')
                qualification = request.data.get('qualification')
                date = request.data.get('date')
                blog_banner = request.data.get('blog_banner')
                author_profile = request.data.get('author_profile')
                
                blog = GeneralBlogs.objects.create(
                    title=title,
                    author=author,
                    qualification=qualification,
                    date=date,
                    blog_banner=blog_banner,
                    author_profile=author_profile
                )
                
                blog_contents = []
                for key in request.data.keys():
                    if key.startswith('blog_contents'):
                        index = key.split('[')[1].split(']')[0]
                        if len(blog_contents) <= int(index):
                            blog_contents.append({})
                        field = key.split('[')[2].split(']')[0]
                        blog_contents[int(index)][field] = request.data.get(key)
                
                print("Extracted blog contents:", blog_contents)

                for content_data in blog_contents:
                    topic = content_data.get('topic')
                    description = content_data.get('description')
                    image = request.data.get(f'blog_contents[{blog_contents.index(content_data)}][image]')
                    
                    content = GeneralBlogsContents.objects.create(
                        blog=blog,
                        topic=topic,
                        description=description,
                        image=image
                    )
                        
        except Exception as e:
            print("Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_201_CREATED)


class BlogListView(APIView):
    def get(self, request):
        blogs = Blogs.objects.all()
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

 
    
    
class GeneralBlogListblog(APIView):
    def get(self, request):
        blogs = GeneralBlogs.objects.all()
        serializer = GeneralBlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class BlogListViewall(generics.ListAPIView):
    queryset = Blogs.objects.prefetch_related('blog_contents').all()
    serializer_class = BlogsSerializer
    
class BlogDeleteView(generics.DestroyAPIView):
    queryset = Blogs.objects.all()
    serializer_class = BlogsSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class GeneralBlogDeleteView(generics.DestroyAPIView):
    queryset = GeneralBlogs.objects.all()
    serializer_class = GeneralBlogsSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

import logging
logger = logging.getLogger(__name__)

 
class GeneralBlogListViewall(generics.ListAPIView):
    queryset = GeneralBlogs.objects.prefetch_related('blog_contents').all()
    serializer_class = GeneralBlogsSerializer

     

 
class GeneralBlogListView(APIView):
    def get(self, request):
        # Use the correct related name here
        blogs = GeneralBlogs.objects.prefetch_related('blog_contents').all()
        serializer = GeneralBlogsSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

 

 
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.db.models import F

from rest_framework.response import Response
from rest_framework import status

from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile

from django.core.files.base import ContentFile
import requests

from io import BytesIO

class BlogUpdateView(UpdateAPIView):
    queryset = Blogs.objects.all()
    serializer_class = BlogsFormSerializer
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        blog = self.get_object()

      
        print("Initial blog object:", blog)

        
        print("Request Data:", request.data)
        print("Request Files:", request.FILES)

      
        blog_contents_data = []
        for key, value in request.data.items():
            if key.startswith('blog_contents'):
                parts = key.split('[')
                index = int(parts[1][:-1])
                field = parts[2][:-1]

                while len(blog_contents_data) <= index:
                    blog_contents_data.append({})

                blog_contents_data[index][field] = value[0] if isinstance(value, list) else value

        print("Parsed blog_contents data:", blog_contents_data)

        # Construct data payload
        data = {
            'forum': request.data.get('forum'),
            'title': request.data.get('title'),
            'author': request.data.get('author'),
            'qualification': request.data.get('qualification'),
            'date': request.data.get('date'),
            'blog_banner': request.FILES.get('blog_banner'),
            'author_profile': request.FILES.get('author_profile'),
            'blog_contents': blog_contents_data,
        }

        print("Constructed data payload:", data)

        # Retain existing files if not provided in the request
        if 'blog_banner' not in request.FILES:
            data['blog_banner'] = blog.blog_banner
        if 'author_profile' not in request.FILES:
            data['author_profile'] = blog.author_profile

        existing_blog_contents = blog.blog_contents.all()
        existing_content_map = {content.topic: content for content in existing_blog_contents}

        updated_blog_contents = []
        for content in data['blog_contents']:
            print("Processing content:", content)
            topic = content.get('topic')
            existing_content = existing_content_map.get(topic)

            if 'image' in content:
                image_url = content['image']
                if isinstance(image_url, str) and image_url.startswith('http'):
                    try:
                        response = requests.get(image_url)
                        response.raise_for_status()
                        content['image'] = ContentFile(response.content, name=image_url.split('/')[-1])

                    except requests.HTTPError:
                        content['image'] = None
                elif not isinstance(content['image'], UploadedFile):
                    if existing_content and existing_content.image:
                        content['image'] = existing_content.image
                    else:
                        content['image'] = None

            updated_blog_contents.append(content)

        print("Updated blog contents:", updated_blog_contents)
        data['blog_contents'] = updated_blog_contents

        # Serialize and save the updated blog data
        serializer = self.get_serializer(blog, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GeneralBlogUpdateView(UpdateAPIView):
    queryset = GeneralBlogs.objects.all()
    serializer_class = BlogsGeneralFormSerializer
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        blog = self.get_object()

        # Print initial blog object data
        print("Initial blog object:", blog)

        # Print all request data
        print("Request Data:", request.data)
        print("Request Files:", request.FILES)

        # Parse blog_contents data
        blog_contents_data = []
        for key, value in request.data.items():
            if key.startswith('blog_contents'):
                parts = key.split('[')
                index = int(parts[1][:-1])
                field = parts[2][:-1]

                while len(blog_contents_data) <= index:
                    blog_contents_data.append({})

                blog_contents_data[index][field] = value[0] if isinstance(value, list) else value

        print("Parsed blog_contents data:", blog_contents_data)

        # Construct data payload without 'forum'
        data = {
            'title': request.data.get('title'),
            'author': request.data.get('author'),
            'qualification': request.data.get('qualification'),
            'date': request.data.get('date'),
            'blog_banner': request.FILES.get('blog_banner'),
            'author_profile': request.FILES.get('author_profile'),
            'blog_contents': blog_contents_data,
        }

        print("Constructed data payload:", data)

        # Retain existing files if not provided in the request
        if 'blog_banner' not in request.FILES:
            data['blog_banner'] = blog.blog_banner
        if 'author_profile' not in request.FILES:
            data['author_profile'] = blog.author_profile

        existing_blog_contents = blog.blog_contents.all()
        existing_content_map = {content.topic: content for content in existing_blog_contents}

        updated_blog_contents = []
        for content in data['blog_contents']:
            print("Processing content:", content)
            topic = content.get('topic')
            existing_content = existing_content_map.get(topic)

            if 'image' in content:
                image_url = content['image']
                if isinstance(image_url, str) and image_url.startswith('http'):
                    try:
                        response = requests.get(image_url)
                        response.raise_for_status()
                        content['image'] = ContentFile(response.content, name=image_url.split('/')[-1])

                    except requests.HTTPError:
                        content['image'] = None
                elif not isinstance(content['image'], UploadedFile):
                    if existing_content and existing_content.image:
                        content['image'] = existing_content.image
                    else:
                        content['image'] = None

            updated_blog_contents.append(content)

        print("Updated blog contents:", updated_blog_contents)
        data['blog_contents'] = updated_blog_contents

        # Serialize and save the updated blog data
        serializer = self.get_serializer(blog, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





        
        
class CertificatesCreate(generics.ListCreateAPIView):
    queryset = Certificates.objects.all()
    serializer_class = CertificatesSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        
        # Extract relevant fields for duplicate check
        event_id = request.data.get('event')
        # Add more fields if needed to uniquely identify a certificate

        # Check for existing certificates
        if Certificates.objects.filter(event_id=event_id).exists():
            return Response(
                {'error': 'A certificate for this event already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use the super().post() to handle the normal create operation
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            print("Error:", e)
            response = Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return response
        
class CertificatesList(generics.ListAPIView):
    queryset = Certificates.objects.all()
    serializer_class = CertificatesSerializer        
        
class GeneralCertificatesList(generics.ListAPIView):
    queryset = GeneralCertificates.objects.all()
    serializer_class = CertificatesSerializer       
        
class CertificatesDeleteView(generics.DestroyAPIView):
    queryset = Certificates.objects.all()
    serializer_class = CertificatesSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
      
class CertificatesDetail(generics.RetrieveUpdateAPIView):
    queryset = Certificates.objects.all()
    serializer_class = CertificatesListSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            print("Request:", request.data)
            print("Updated instance:", serializer.data)
            return Response(serializer.data)
        except Exception as e:
            print("Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
        
        
class BannerListCreate(generics.ListCreateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()        
        

class BannerUpdateView(generics.UpdateAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

class BannerDeleteView(generics.DestroyAPIView):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer
        
        
class NewsListCreate(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()        
        

class NewsUpdateView(generics.UpdateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer 


class NewsDeleteView(generics.DestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer


class ForumMemberList(generics.ListAPIView):
    serializer_class = ForumMemberSerializer

    def get_queryset(self):
        forum_id = self.kwargs.get('forum_id')
        print("ppp",forum_id)
        return ForumMember.objects.filter(forum_id=forum_id)              
        
        
          
class AddBoardMember(APIView):
    def post(self, request, format=None):
        board_member_id = request.data.get('id')
        if board_member_id:
            try:
                board_member = BoardMember.objects.get(id=board_member_id)
            except BoardMember.DoesNotExist:
                return Response({"message": "Board member not found."}, status=status.HTTP_404_NOT_FOUND)
        else:
            board_member = BoardMember.objects.create()  # Create a new board member if ID not provided

        serializer = BoardMemberSerializer(board_member, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ForumListView(APIView):
    def get(self, request, format=None):
    
        forums = Forum.objects.all()
       
     
        forums_with_members = ForumMember.objects.values_list('forum_id', flat=True).distinct()
       

       
        filtered_forums = forums.exclude(id__in=forums_with_members)

        serializer = ForumSerializer(filtered_forums, many=True)
       
        return Response(serializer.data)


class ForumLisMembertView(APIView):
    def get(self, request, format=None):
       
        forums = Forum.objects.all()
        
       
        forums_with_members = ForumMember.objects.values_list('forum_id', flat=True).distinct()
        
       
        filtered_forums = forums.filter(id__in=forums_with_members)
        
     
        serializer = ForumSerializer(filtered_forums, many=True)
 
        return Response(serializer.data)


class BoardListCreate(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        
        serializer.save()


class BoardUpdateView(generics.UpdateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

class BoardDeleteView(generics.DestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer



class BoardListView(APIView):
    def get(self, request, format=None):
        boards = Board.objects.all()
      
        boards_with_members = BoardMember.objects.values_list('board_id', flat=True).distinct()
      
        filtered_boards = boards.exclude(id__in=boards_with_members)
        serializer = BoardSerializer(filtered_boards, many=True)
        
        return Response(serializer.data)
    

class BoardLisMembertView(APIView):
    def get(self, request, format=None):
               
        boards = Board.objects.all() 
        print("All boards:", boards)     
        boards_with_members = BoardMember.objects.values_list('board_id', flat=True).distinct() 
        print("Boards with members:", boards_with_members)    
        filtered_boards = boards.filter(id__in=boards_with_members)    
        serializer = BoardSerializer(filtered_boards, many=True)
        print("serializer.data 2",serializer.data)
        return Response(serializer.data)
    
class BoardExcludeView(APIView):
    def get(self, request, board_id):
        try:
            all_members = Board.objects.all()
            board_members = BoardMember.objects.filter(board=board_id).values_list('member_id', flat=True)
            members_not_in_board = all_members.exclude(id__in=board_members)
            serializer = MemeberSerializer(members_not_in_board, many=True)
            print("serializer",serializer.data)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BoardMemberCreateView(generics.CreateAPIView):
    serializer_class = BoardMemberSerializer

    def create(self, request, *args, **kwargs):
        board_id = request.data.get('board')
        selected_members = request.data.get('members', [])

        # Check if the board exists
        try:
            board = Board.objects.get(pk=board_id)
        except Board.DoesNotExist:
            return Response({"error": "Board does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Check if a BoardMember already exists for this board
        existing_board_member = BoardMember.objects.filter(board_id=board_id).first()
        if existing_board_member:
            return Response({"error": "Board member already exists for this board."}, status=status.HTTP_400_BAD_REQUEST)

        # Create the BoardMember
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board_member_instance = serializer.save()

        # Associate selected members with the BoardMember
        board_member_instance.member.add(*selected_members)

        return Response({"message": "Board member created successfully."}, status=status.HTTP_201_CREATED)


class BoardMemberListView(APIView):
    def get(self, request, board_id):
        try:           
            board_members = BoardMember.objects.filter(board=board_id)            
            serializer = BoardMemberSerializer(board_members, many=True)
       
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class BoardMemberView(APIView):
    def put(self, request, board_id, format=None):  
        print("request", request.data)
        try:
            board_member = BoardMember.objects.get(board_id=board_id)
        except BoardMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        selected_members = request.data.get('members', [])
        deleted_members = request.data.get('deleted_members', [])
        print("kkkkk", selected_members)
        print("DDDDD", deleted_members)
        
        if selected_members:
            board_member.member.add(*selected_members)

        if deleted_members:
            board_member.member.remove(*deleted_members)

        for member_id in deleted_members:
            if member_id in selected_members:
                board_member.member.add(member_id)

        serializer = BoardMemberSerializer(board_member)
        print("ssssss", serializer.data)
        return Response(serializer.data)
    
    
from django.db.models import Count
from django.db.models.functions import Lower

class AllBoardMembersView(APIView):
    def get(self, request):
     
        board = Board.objects.filter(title="Board of Directors").first()

        if not board:
            return Response({'detail': 'Board of Directors not found'}, status=404)

        board_members = BoardMember.objects.filter(board=board).prefetch_related('member')

        # Collect all members for the board
        members = []
        for board_member in board_members:
            members.extend(board_member.member.all())

        # Serialize the member data
        serializer = MemeberSerializer(members, many=True)
        return Response(serializer.data)

class CommitteeMembersView(APIView):
    def get(self, request):
     
        board = Board.objects.filter(title="Committees").first()

        if not board:
            return Response({'detail': 'Committees board not found'}, status=404)

        
        board_members = BoardMember.objects.filter(board=board).prefetch_related('member')

   
        members = []
        for board_member in board_members:
            members.extend(board_member.member.all())
 
        unique_members = list({member.id: member for member in members}.values())

      
        serializer = MemeberSerializer(unique_members, many=True)
        return Response(serializer.data)

from django.http import JsonResponse
from django.views import View
from .models import Member  # Ensure you have the Member model

class MemberDetailViewBySlug(View):
    def get(self, request, slug):
        try:
            member = Member.objects.get(slug=slug)
            data = {
                'id': member.id,
                'name': member.name,
                'image': member.image.url if member.image else None,
                'qualification': member.qualification,
                'recentJobTitle': member.recent_job_title,
                'additionalJobTitles': member.additional_job_titles,
                'previousWorkExperience': member.previous_work_experience,
                'publications': member.publications,
                'conference': member.conference,
                'additionalInformation': member.additional_information,
                'achievements': member.achievements,
                'areasOfInterest': member.areas,
                'linkedin' : member.linkedin, 
            }
        
            return JsonResponse(data)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)


from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import get_object_or_404

class EventForumListView(APIView):
    def calculate_end_date(self, event):
        """
        Calculates the start and end dates of the event based on its single events.
        """
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_multi_event_times(self, event):
        """
        Calculates the starting time of the first MultiEvent and ending time of the last MultiEvent
        when days = 1 for the given event.
        """
        single_event = event.single_events.filter(day=1).first()
        if single_event:
            multi_events = single_event.multi_events.all()
            if multi_events.exists():
                start_time = multi_events.first().starting_time
                end_time = multi_events.last().ending_time
                return start_time, end_time
        return None, None

    def get_event_status(self, event):
        """
        Determines the status of the event based on current datetime and multi-event times,
        with a 15-minute buffer for live status.
        """
        current_datetime = timezone.now()  # Get the current time
        start_date, end_date = self.calculate_end_date(event)
        start_time, end_time = self.calculate_multi_event_times(event)

        if start_date and end_date and start_time and end_time:
            # Combine date and time to get the full datetime for start and end
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, end_time))

            # Adding the 15-minute buffer before the start and after the end
            live_start_datetime = event_start_datetime - timedelta(minutes=15)
            live_end_datetime = event_end_datetime + timedelta(minutes=15)

            # Determine event status based on the current time and the time buffers
            if current_datetime < live_start_datetime:
                return "Upcoming"  # Before 15 minutes of the first multi-event's start time
            elif live_start_datetime <= current_datetime <= live_end_datetime:
                return "Live"  # Within the 15 minutes before start and 15 minutes after the last end time
            elif current_datetime > live_end_datetime:
                return "Completed"  # After 15 minutes of the last multi-event's end time
        return "Upcoming"

    def get(self, request, slug):
        """
        Retrieves all events for a specific forum, categorizes them based on status,
        and returns serialized data.
        """
        forum = get_object_or_404(Forum, slug=slug)
        events = Event.objects.filter(forum=forum)

        live_events_data = []
        upcoming_events_data = []
        completed_events_data = []

        for event in events:
            # Determine event status
            status = self.get_event_status(event)

            # Calculate start and end dates
            start_date, end_date = self.calculate_end_date(event)

            # Calculate start and end times of MultiEvent for days = 1
            start_time, end_time = self.calculate_multi_event_times(event)

            # Serialize event data
            event_data = EventListSerializer(event).data
            event_data['start_date'] = start_date
            event_data['end_date'] = end_date
            event_data['times'] = {
                'start_time': start_time,
                'end_time': end_time
            }

            # Append to appropriate list based on status
            if status == "Live":
                live_events_data.append(event_data)
            elif status == "Upcoming":
                upcoming_events_data.append(event_data)
            else:
                completed_events_data.append(event_data)

        return Response({
            'forum': {
                'title': forum.title,
                'description': forum.description,
                'image': forum.image.url if forum.image else None,
            },
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })

        
class BlogForumListView(APIView):
    def get(self, request, slug):
         
        blogs = Blogs.objects.filter(forum__slug=slug)
        print("blogs", blogs)
        serializer = BlogSerializer(blogs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class EventForumYearView(APIView):
    def calculate_event_dates(self, event):
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def get_event_year(self, event):
        start_date, _ = self.calculate_event_dates(event)
        if start_date:
            return start_date.year
        return None

    def serialize_event(self, event):
        start_date, end_date = self.calculate_event_dates(event)
        event_data = EventListSerializer(event).data
        event_data['start_date'] = start_date
        event_data['end_date'] = end_date
        return event_data

    def get(self, request, slug):
        forum = get_object_or_404(Forum, slug=slug)
        events = Event.objects.filter(forum=forum)

        year_events = {}

        for event in events:
            event_year = self.get_event_year(event)
            if event_year in [2024, 2023, 2022, 2021]:  # Filter events for specific years
                if event_year not in year_events:
                    year_events[event_year] = []
                year_events[event_year].append(self.serialize_event(event))

        forum_data = {
            'title': forum.title,
            'description': forum.description,
            'image': forum.image.url if forum.image else None,
        }

        return Response({
            'forum': forum_data,
            'events': year_events,
        })


class BlogForumYearView(APIView):
    def get(self, request, slug):
  
        years = [2024, 2023, 2022]
        
     
        forum = get_object_or_404(Forum, slug=slug)
        
      
        blogs = Blogs.objects.filter(forum=forum, date__year__in=years)
        
     
        serializer = BlogSerializer(blogs, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    
class EventTodayView(APIView):
    def get(self, request, slug):
    
        forum = get_object_or_404(Forum, slug=slug)
    
        current_date = datetime.now().date()
        
 
        events = Event.objects.filter(forum=forum, single_events__date=current_date).distinct()
        
    
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'forum': {
                'title': forum.title,
                'description': forum.description,
                'image': forum.image.url if forum.image else None,
            },
            'events': events_data,
        }, status=status.HTTP_200_OK)

from django.utils.timezone import now, timedelta


       
class EventThisWeekView(APIView):
    def get(self, request, slug):
        forum = get_object_or_404(Forum, slug=slug)
        
        
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        
        events = Event.objects.filter(forum=forum, single_events__date__range=[start_of_week, end_of_week]).distinct()
        
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'forum': {
                'title': forum.title,
                'description': forum.description,
                'image': forum.image.url if forum.image else None,
            },
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
import calendar       


 
from datetime import timedelta

class EventThisMonthView(APIView):
    def get(self, request, slug):
        forum = get_object_or_404(Forum, slug=slug)
        
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Calculate the end of the month
        end_of_month = start_of_month.replace(day=calendar.monthrange(start_of_month.year, start_of_month.month)[1])
        
        # Filter events for the current month only
        events = Event.objects.filter(
            forum=forum, 
            single_events__date__gte=start_of_month, 
            single_events__date__lt=end_of_month + timedelta(days=1)  # Filter out events occurring after the end of the month
        ).distinct()
        
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'forum': {
                'title': forum.title,
                'description': forum.description,
                'image': forum.image.url if forum.image else None,
            },
            'events': events_data,
        }, status=status.HTTP_200_OK)


class EventThisYearView(APIView):
    def get(self, request, slug):
        forum = get_object_or_404(Forum, slug=slug)
        
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        
        # Filter events for the current year only
        events = Event.objects.filter(
            forum=forum, 
            single_events__date__gte=start_of_year, 
            single_events__date__lte=end_of_year
        ).distinct()
        
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'forum': {
                'title': forum.title,
                'description': forum.description,
                'image': forum.image.url if forum.image else None,
            },
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
        
class BlogDetailView(APIView):
    def get(self, request, slug):
        blog = get_object_or_404(Blogs, slug=slug)
        serializer = BlogSerializer(blog)
        print("ssss",serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class BlogGeneralDetailView(APIView):
    def get(self, request, slug):
        blog = get_object_or_404(GeneralBlogs, slug=slug)
        serializer = GeneralBlogSerializer(blog)
        print("ssss",serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
class EventUserToday(APIView):
    def get(self, request):
        current_date = timezone.now().date()
        events = Event.objects.filter(single_events__date=current_date).distinct()

        events_data = EventListSerializer(events, many=True).data

        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
        
class EventUserThisWeek(APIView):
    def get(self, request):
        today = now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        events = Event.objects.filter(single_events__date__range=[start_of_week, end_of_week]).distinct()
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
class EventThisMonthUser(APIView):
    def get(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Calculate the end of the month
        end_of_month = start_of_month.replace(day=calendar.monthrange(start_of_month.year, start_of_month.month)[1])
        
        # Filter events for the current month only
        events = Event.objects.filter(
            single_events__date__gte=start_of_month, 
            single_events__date__lt=end_of_month + timedelta(days=1)  # Filter out events occurring after the end of the month
        ).distinct()
        
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
        
class EventThisYearUser(APIView):
    def get(self, request):
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        
        # Filter events for the current year only
        events = Event.objects.filter(
            single_events__date__gte=start_of_year, 
            single_events__date__lte=end_of_year
        ).distinct()
        
        events_data = EventListSerializer(events, many=True).data
        
        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
        
        
        
class EventUpdateView(APIView):
    @transaction.atomic
    def put(self, request, event_id):
        try:
            print("Request Data:", request.data)
            
            # Fetch existing event
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

            # Extract event data from request
            event_data = {
                'event_name': request.data.get('event_name'),
                'date': None,
                'days': int(request.data.get('days')),  
                'forum': request.data.get('forum'),
                'speakers': [speaker.strip('"') for speaker in request.data.getlist('speakers[]')],
                'banner': request.data.get('banner')
            }

            # Handle date format conversion
            date_str = request.data.get('date')
            if date_str:
                event_data['date'] = datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')

            start_date = datetime.strptime(event_data['date'], '%Y-%m-%d') if event_data['date'] else None
            dates = [start_date + timedelta(days=i) for i in range(event_data['days'])] if start_date else []

            print("Event Data before serialization:", event_data)

            # Validate forum
            forum_id = event_data.get('forum')
            if not Forum.objects.filter(id=forum_id).exists():
                return Response({'error': 'Invalid forum ID'}, status=status.HTTP_400_BAD_REQUEST)

            event_serializer = EventSerializer(event, data=event_data, partial=True)
            if event_serializer.is_valid():
                event = event_serializer.save()
            else:
                print("Event Serializer Errors:", event_serializer.errors)
                return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            single_events_data = request.data.getlist('single_events[]')
            print("Single Events Data:", single_events_data)

            # Clear existing single events and multi events
            SingleEvent.objects.filter(event=event).delete()

            for date_index, date in enumerate(dates):
                single_event_data_dict = json.loads(single_events_data[date_index])
                single_event_data_dict['date'] = date.strftime('%Y-%m-%d')
                single_event_data_dict['day'] = date_index + 1  # Assign day number
                single_serializer = SingleEventSerializer(data=single_event_data_dict)
                if single_serializer.is_valid():
                    single_instance = single_serializer.save(event=event, date=date, day=date_index + 1)
                else:
                    print("Single Event Serializer Errors:", single_serializer.errors)
                    return Response(single_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                multi_events_data = single_serializer.validated_data.get('multi_events', [])
                for multi_event_data in multi_events_data:
                    multi_event_data['single_event'] = single_instance.id
                    multi_serializer = MultiEventSerializer(data=multi_event_data, context={'single_event': single_instance})
                    if multi_serializer.is_valid():
                        multi_serializer.save()
                    else:
                        print("Multi Event Serializer Errors:", multi_serializer.errors)
                        return Response(multi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Event and associated data updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class AddGalleryView(generics.CreateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    parser_classes = [MultiPartParser, FormParser]

    def perform_create(self, serializer):
        serializer.save()
        


class GetGalleryView(generics.ListAPIView):
    serializer_class = GallerySerializer
    queryset = Gallery.objects.all()

    def get_queryset(self):
        title = self.request.query_params.get('title', None)
        if title:
            return Gallery.objects.filter(title=title)
        return Gallery.objects.all()
    
    
 

class UpdateGalleryView(generics.UpdateAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GalleryUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, *args, **kwargs):
        print("request data:", request.data)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            print("updated serializer data:", serializer.data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        print("serializer errors:", serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class DeleteGalleryView(generics.DestroyAPIView):
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer
    lookup_url_kwarg = 'gallery_id'  # URL keyword argument name for the gallery ID

    def delete(self, request, *args, **kwargs):
        gallery_id = kwargs.get(self.lookup_url_kwarg)
        try:
            gallery = self.get_queryset().get(id=gallery_id)
        except Gallery.DoesNotExist:
            return Response({'error': 'Gallery not found'}, status=status.HTTP_404_NOT_FOUND)

        gallery.delete()
        return Response({'message': 'Gallery deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


class EventDeleteAPIView(APIView):
    def delete(self, request, event_id):
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework.permissions import IsAuthenticated      
 
class SingleEventListAllView(APIView):
    def get(self, request):
        single_events = SingleEvent.objects.all()
        serializer = SingleAllEventSerializer(single_events, many=True)
        return Response(serializer.data)
    
class SingleGeneralEventListAllView(APIView):
    def get(self, request):
        single_events = GeneralSingleEvent.objects.all()
        serializer = GeneralSingleAllEventSerializer(single_events, many=True)
        return Response(serializer.data)
        
    
class UploadAttachmentView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        single_event_id = request.data.get('single_event')

        if not file or not single_event_id:
            return Response({'error': 'File and Single Event are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Attachment instance
        attachment = Attachment.objects.create(single_event_id=single_event_id, file=file)

        serializer = AttachmentSerializer(attachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class UpdateAttachmentView(APIView):
    def put(self, request, pk, format=None):
        try:
            attachment = Attachment.objects.get(pk=pk)
        except Attachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttachmentSerializer(attachment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)





 
class GeneralAttachmentsBySingleEventView(generics.ListAPIView):
    serializer_class = GeneralAttachmentSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if slug:
            try:
                event = GeneralEvent.objects.get(slug=slug)
                queryset = GeneralAttachment.objects.filter(single_event__event=event)  # Filter by event, not by ID
                print(f'GeneralAttachmentsBySingleEventView: Fetched {queryset.count()} attachments for event_slug={slug}')
                for attachment in queryset:
                    print(f'Attachment ID: {attachment.id}, File: {attachment.file}')
                return queryset
            except GeneralEvent.DoesNotExist:
                print(f'GeneralAttachmentsBySingleEventView: Event with slug {slug} does not exist')
        else:
            print('GeneralAttachmentsBySingleEventView: No event_slug provided')
        return GeneralAttachment.objects.none()


class AttachmentsBySingleEventView(generics.ListAPIView):
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        if slug:
            try:
                event = Event.objects.get(slug=slug)
                queryset = Attachment.objects.filter(single_event__event=event)  # Filter by event, not by ID
                print(f'AttachmentsBySingleEventView: Fetched {queryset.count()} attachments for event_slug={slug}')
                for attachment in queryset:
                    print(f'Attachment ID: {attachment.id}, File: {attachment.file}')
                return queryset
            except Event.DoesNotExist:
                print(f'AttachmentsBySingleEventView: Event with slug {slug} does not exist')
        else:
            print('AttachmentsBySingleEventView: No event_slug provided')
        return Attachment.objects.none()


 
    
    
class ListAttachmentsView(generics.ListAPIView):
    queryset = Attachment.objects.all()
    serializer_class = AttachmentSerializer



class AttachmentDeleteAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        try:
            attachment = Attachment.objects.get(id=kwargs['pk'])
        except Attachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        attachment.delete()
        return Response({'message': 'Attachment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)


  
class AssociateFileWithUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received request data:", request.data)  # Ensure you print the correct fields
        attachment_id = request.data.get('attachmentId')
        single_event_id = request.data.get('singleEventId')  # Change to singleEventId

        if not attachment_id or not single_event_id:
            print("Missing attachmentId or singleEventId")  # Debug message
            return Response({'error': 'attachmentId and singleEventId are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            attachment = Attachment.objects.get(id=attachment_id)
            single_event = SingleEvent.objects.get(id=single_event_id)
        except Attachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
        except SingleEvent.DoesNotExist:
            return Response({'error': 'SingleEvent not found'}, status=status.HTTP_404_NOT_FOUND)

        association, created = UserFileAssociation.objects.get_or_create(
            user=request.user,
            attachment=attachment
        )
        
        return Response({'message': 'File associated with user successfully'}, status=status.HTTP_200_OK)

class UserAttachmentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        user = self.request.user
        # Get attachment IDs associated with the user
        attachment_ids = UserFileAssociation.objects.filter(user=user).values_list('attachment_id', flat=True)
        # Fetch the full Attachment instances
        return Attachment.objects.filter(id__in=attachment_ids)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'attachments': serializer.data}, status=status.HTTP_200_OK)
    
    
class GeneralUserAttachmentsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = GeneralAttachmentSerializer

    def get_queryset(self):
        user = self.request.user
        # Get attachment IDs associated with the user
        attachment_ids = GeneralUserFileAssociation.objects.filter(user=user).values_list('attachment_id', flat=True)
        # Fetch the full Attachment instances
        return GeneralAttachment.objects.filter(id__in=attachment_ids)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({'attachments': serializer.data}, status=status.HTTP_200_OK)
    
class AttachmentUpdateAPIView(APIView):
    def put(self, request, *args, **kwargs):
        try:
            attachment = Attachment.objects.get(id=kwargs['pk'])
        except Attachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = AttachmentSerializer(attachment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

 

from rest_framework import viewsets    
class GeneralEventListCreate(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            print("Request Data:", request.data)

            speakers_list = request.data.getlist('speakers')
            print("Extracted Speakers List:", speakers_list)

            event_data = {
                'event_name': request.data.get('event_name'),
                'date': None,
                'days': int(request.data.get('days', 1)),
                'speakers': speakers_list,
                'banner': request.data.get('banner')
            }

            date_str = request.data.get('date')
            if date_str:
                try:
                    event_data['date'] = datetime.strptime(date_str, '%d-%m-%Y').strftime('%Y-%m-%d')
                except ValueError:
                    return Response({'error': 'Invalid date format. Use DD-MM-YYYY.'}, status=status.HTTP_400_BAD_REQUEST)

            start_date = datetime.strptime(event_data['date'], '%Y-%m-%d') if event_data['date'] else None
            dates = [start_date + timedelta(days=i) for i in range(event_data['days'])] if start_date else []

            print("Event Data before serialization:", event_data)

            event_serializer = GeneralEventSerializer(data=event_data)
            if event_serializer.is_valid():
                print("Event Serializer:", event_serializer)
                event = event_serializer.save()

                single_events_data = request.data.getlist('single_events[]')
                print("Single Events Data:", single_events_data)

                for date_index, date in enumerate(dates):
                    single_event_data_dict = json.loads(single_events_data[date_index])
                    single_event_data_dict['date'] = date.strftime('%Y-%m-%d')
                    single_event_data_dict['day'] = date_index + 1
                    single_serializer = GeneralSingleEventSerializer(data=single_event_data_dict)
                    if single_serializer.is_valid():
                        single_instance = single_serializer.save(event=event, date=date, day=date_index + 1)

                        multi_events_data = single_serializer.validated_data.get('multi_events', [])
                        for multi_event_data in multi_events_data:
                            existing_multi_event = GeneralMultiEvent.objects.filter(
                                single_event=single_instance,
                                starting_time=multi_event_data['starting_time'],
                                ending_time=multi_event_data['ending_time']
                            ).first()

                            if not existing_multi_event:
                                multi_event_data['single_event'] = single_instance.id
                                multi_serializer = GeneralMultiEventSerializer(data=multi_event_data, context={'single_event': single_instance})
                                if multi_serializer.is_valid():
                                    multi_serializer.save()
                                else:
                                    print("Multi Event Serializer Errors:", multi_serializer.errors)
                                    return Response(multi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        print("Single Event Serializer Errors:", single_serializer.errors)
                        return Response(single_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                return Response({'message': 'Event and associated data created successfully'}, status=status.HTTP_201_CREATED)

            else:
                print("Event Serializer Errors:", event_serializer.errors)
                return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class GeneralEventListAllView(APIView):
    def get(self, request):
       
        events = GeneralEvent.objects.all()
        serializer = GeneralEventListSerializer(events, many=True)
 
        return Response(serializer.data)
    
    
class GeneralEventDeleteAPIView(APIView):
    def delete(self, request, event_id):
        try:
            event = GeneralEvent.objects.get(pk=event_id)
            event.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

# views.py
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from django.utils.dateparse import parse_date
from django.db import transaction
import json
from datetime import timedelta

from .models import Event, SingleEvent, MultiEvent, Forum
from .serializers import EventSerializer

class GeneralEventUpdateAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)  # Ensure to include parsers for handling file uploads

    @transaction.atomic
    def put(self, request, event_id):
        try:
            print("Request Data:", request.data)
            print("Request Files:", request.FILES)  # Debug: Print files in request

            # Fetch the event to update
            event = get_object_or_404(GeneralEvent, id=event_id)
            speakers_list = request.data.getlist('speakers')
            print("Extracted Speakers List:", speakers_list)

            speakers_list = [int(speaker_id) for speaker_id in speakers_list]

            # Prepare data for updating the event
            event_name = request.data.get('event_name')
            date_str = request.data.get('date')
            days = int(request.data.get('days', 1))

            # Handle file upload for banner
            if 'banner' in request.FILES:
                event.banner = request.FILES['banner']  # Use request.FILES to get the uploaded file

            # Validate and parse the date
            if date_str:
                try:
                    event_date = parse_date(date_str)
                    if not event_date:
                        raise ValueError("Invalid date format.")
                except ValueError:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                event_date = None

            # Update event fields
            event.event_name = event_name
            event.date = event_date
            event.days = days

            event.save()  # Save the updated event before updating related data

            # Update the speakers associated with the event
            event.speakers.set(speakers_list)

            # **Key Change**: Remove deletion of all SingleEvents
            single_events_data = json.loads(request.data.get('single_events', '[]'))
            print("Single Events Data:", single_events_data)

            # Create dates for the single events
            dates = [event_date + timedelta(days=i) for i in range(days)] if event_date else []
            if len(single_events_data) < len(dates):
                return Response({'error': 'Insufficient single events data.'}, status=status.HTTP_400_BAD_REQUEST)

            for date_index, date in enumerate(dates):
                single_event_data = single_events_data[date_index]

                # **Key Change**: Update or create SingleEvent instead of deleting all
                single_event, created = GeneralSingleEvent.objects.update_or_create(
                    event=event,
                    day=date_index + 1,
                    defaults={
                        'date': date.strftime('%Y-%m-%d'),
                        'youtube_link': single_event_data.get('youtube_link'),
                        'points': single_event_data.get('points'),
                        'highlights': single_event_data.get('highlights', []),
                    }
                )

                # Remove attachment handling from this section

                # Handle MultiEvent for each SingleEvent
                GeneralMultiEvent.objects.filter(single_event=single_event).delete()  # You may want to handle this more carefully
                for multi_event_data in single_event_data.get('multi_events', []):
                    single_speaker_id = multi_event_data.get('single_speaker')
                    if isinstance(single_speaker_id, dict):
                        single_speaker_id = single_speaker_id.get('id')
                    
                    GeneralMultiEvent.objects.create(
                        single_event=single_event,
                        starting_time=multi_event_data.get('starting_time'),
                        ending_time=multi_event_data.get('ending_time'),
                        topics=multi_event_data.get('topics'),
                        single_speaker_id=single_speaker_id,
                    )

            return Response({'message': 'Event and associated data updated successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from django.utils import timezone
from datetime import datetime

from django.utils import timezone
from datetime import datetime

from datetime import timedelta, datetime
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

from django.utils import timezone
from datetime import datetime, timedelta

class GeneralEventListView(APIView):
    def calculate_end_date(self, event):
        """
        Calculates the start and end dates of the event based on its single events.
        """
        single_events = event.general_single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_multi_event_times(self, event):
        """
        Calculates the earliest starting time and latest ending time for all MultiEvents
        across all SingleEvents in the event.
        """
        earliest_start_time = None
        latest_end_time = None

        for single_event in event.general_single_events.all():
            multi_events = single_event.general_multi_events.all()
            for multi_event in multi_events:
                if earliest_start_time is None or multi_event.starting_time < earliest_start_time:
                    earliest_start_time = multi_event.starting_time
                if latest_end_time is None or multi_event.ending_time > latest_end_time:
                    latest_end_time = multi_event.ending_time

        return earliest_start_time, latest_end_time

    def calculate_last_single_event_end_time(self, event):
        """
        Calculates the ending time of the last multi-event in the last single event.
        """
        single_events = event.general_single_events.all()

        if not single_events.exists():
            return None

        # Get the last single event
        last_single_event = single_events.last()

        # Get the last multi-event in the last single event
        last_multi_event = last_single_event.general_multi_events.last()

        # Return the ending time of the last multi-event if it exists
        if last_multi_event:
            return last_multi_event.ending_time
        return None

    def get_event_status(self, event):
        """
        Determines the status of the event based on current datetime and the ending time of the 
        last multi-event in the last single event.
        """
        current_datetime = timezone.now()
        start_date, end_date = self.calculate_end_date(event)
        start_time, _ = self.calculate_multi_event_times(event)

        # Get the ending time of the last multi-event in the last single event
        last_multi_event_end_time = self.calculate_last_single_event_end_time(event)

        if start_date and end_date and start_time and last_multi_event_end_time:
            # Make the event start datetime timezone-aware
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))

            # Use the end date and the ending time of the last multi-event for event completion
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, last_multi_event_end_time))

            # Add 15-minute buffers for live status
            live_start_datetime = event_start_datetime - timedelta(minutes=15)
            live_end_datetime = event_end_datetime + timedelta(minutes=15)

            print(f"Current Time: {current_datetime}")
            print(f"Event Start Time: {event_start_datetime}")
            print(f"Event End Time (based on last multi-event): {event_end_datetime}")
            print(f"Fifteen Minutes Before Start: {live_start_datetime}")
            print(f"Fifteen Minutes After End: {live_end_datetime}")

            # Determine the event status
            if current_datetime < live_start_datetime:
                return "Upcoming"
            elif live_start_datetime <= current_datetime <= live_end_datetime:
                return "Live"
            elif current_datetime > live_end_datetime:
                return "Completed"

        return "Upcoming"  # Default to upcoming if dates are missing

    def get(self, request):
        """
        Retrieves all events, categorizes them based on status, and returns serialized data.
        """
        events = GeneralEvent.objects.all()
        live_events_data = []
        upcoming_events_data = []
        completed_events_data = []

        for event in events:
            # Calculate event status
            status = self.get_event_status(event)

            # Calculate event dates and times
            start_date, end_date = self.calculate_end_date(event)
            start_time, _ = self.calculate_multi_event_times(event)

            # Serialize event data and add start/end times
            event_data = GeneralEventListSerializer(event).data
            event_data['start_date'] = start_date
            event_data['end_date'] = end_date
            event_data['times'] = {
                'start_time': start_time,
                'end_time': self.calculate_last_single_event_end_time(event)  # Updated to use the last multi-event's end time
            }

            # Categorize events based on their status
            if status == "Live":
                live_events_data.append(event_data)
            elif status == "Upcoming":
                upcoming_events_data.append(event_data)
            else:
                completed_events_data.append(event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })

 
 

class GeneralSingleEventDetailView(APIView):
    def get(self, request, slug):
        try:
            event = get_object_or_404(
                GeneralEvent.objects.prefetch_related('speakers', 'general_single_events__general_multi_events'),
                slug=slug
            )
            serialized_data = GeneralEventListSerializer(event, context={'request': request}).data
            serialized_single_events = []
            single_events = event.general_single_events.all().order_by('day')

            for single_event in single_events:
                single_event_dict = GeneralRetrieveSingleEventSerializer(single_event).data
                single_event_dict['day'] = single_event.day

                multi_events = single_event.general_multi_events.all().order_by('starting_time')

                if multi_events.exists():
                    first_multi_event = multi_events.first()
                    last_multi_event = multi_events.last()

                    
                    if first_multi_event.starting_time:
                        single_event_dict['first_multi_event_start'] = str(first_multi_event.starting_time)
                    if last_multi_event.ending_time:
                        single_event_dict['last_multi_event_end'] = str(last_multi_event.ending_time)

                serialized_single_events.append(single_event_dict)

            if single_events.exists():
                serialized_data['start_date'] = single_events.first().date.strftime('%Y-%m-%d')
                serialized_data['end_date'] = single_events.last().date.strftime('%Y-%m-%d')
            else:
                serialized_data['start_date'] = None
                serialized_data['end_date'] = None

            serialized_data['single_events'] = serialized_single_events

            return Response(serialized_data)

        except GeneralEvent.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

class GeneralEventSpeakersView(APIView):
    def get(self, request, slug):
        event = get_object_or_404(GeneralEvent, slug=slug)
        serializer = GeneralEventSpeakerSerializer(event)
       
        return Response(serializer.data) 
    
    
class GeneralSingleEventDetailView(APIView):
    def get(self, request, slug):
        try:
            # Use the correct related names
            event = get_object_or_404(
                GeneralEvent.objects.prefetch_related('speakers', 'general_single_events__general_multi_events'),
                slug=slug
            )
            
            serialized_data = GeneralEventListSerializer(event, context={'request': request}).data
            
            serialized_single_events = []
            single_events = event.general_single_events.all().order_by('day')  # Use correct related_name

            for single_event in single_events:
                single_event_dict = GeneralRetrieveSingleEventSerializer(single_event).data
                single_event_dict['day'] = single_event.day

                multi_events = single_event.general_multi_events.all().order_by('starting_time')  # Use correct related_name

                if multi_events.exists():
                    first_multi_event = multi_events.first()
                    last_multi_event = multi_events.last()

                    if first_multi_event.starting_time:
                        single_event_dict['first_multi_event_start'] = str(first_multi_event.starting_time)
                    if last_multi_event.ending_time:
                        single_event_dict['last_multi_event_end'] = str(last_multi_event.ending_time)

                serialized_single_events.append(single_event_dict)

            if single_events.exists():
                serialized_data['start_date'] = single_events.first().date.strftime('%Y-%m-%d')
                serialized_data['end_date'] = single_events.last().date.strftime('%Y-%m-%d')
            else:
                serialized_data['start_date'] = None
                serialized_data['end_date'] = None

            serialized_data['single_events'] = serialized_single_events

            return Response(serialized_data)

        except GeneralEvent.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)




class GeneralSingleDetailView(APIView):
    def get(self, request, slug):
        try:
            event = get_object_or_404(
                GeneralEvent.objects.prefetch_related(
                    'general_single_events__general_multi_events'  # Ensure related data is fetched
                ),
                slug=slug
            )
            serialized_data = GeneralEventListSerializer(event, context={'request': request}).data

            serialized_single_events = []
            current_date = timezone.now().date()  # Get the current date

            # Sort single_events by date
            sorted_single_events = sorted(event.general_single_events.all(), key=lambda se: se.date)

            # Initialize start_date and end_date
            start_date = None
            end_date = None

            for index, single_event in enumerate(sorted_single_events, start=1):
                # Serialize single event
                serialized_single_event = {
                    'id': single_event.id,
                    'highlights': single_event.highlights.split(', '),  # Convert back to list if needed
                    'youtube_link': single_event.youtube_link,
                    'points': str(single_event.points) if single_event.points else None,
                    'date': single_event.date.strftime('%Y-%m-%d'),
                    'day': index,
                    'is_live_or_completed': single_event.date <= current_date,
                }

                # Handle multi-events within the single event
                multi_events = single_event.general_multi_events.all().order_by('starting_time')
                if multi_events.exists():
                    first_multi_event = multi_events.first()
                    last_multi_event = multi_events.last()

                    # Assign start and end times directly from MultiEvent
                    serialized_single_event['first_multi_event_start'] = str(first_multi_event.starting_time) if first_multi_event.starting_time else None
                    serialized_single_event['last_multi_event_end'] = str(last_multi_event.ending_time) if last_multi_event.ending_time else None
                
                serialized_single_events.append(serialized_single_event)

            # Set start_date and end_date based on the earliest and latest single events
            if sorted_single_events:
                start_date = sorted_single_events[0].date.strftime('%Y-%m-%d')
                end_date = sorted_single_events[-1].date.strftime('%Y-%m-%d')

            serialized_data['start_date'] = start_date
            serialized_data['end_date'] = end_date
            serialized_data['single_events'] = serialized_single_events

            return Response(serialized_data)
               
        except GeneralEvent.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
        
class GeneralCertificatesCreate(generics.ListCreateAPIView):
    queryset = GeneralCertificates.objects.all()
    serializer_class = GeneralCertificatesSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        
        # Extract relevant fields for duplicate check
        event_id = request.data.get('event')
        # Add more fields if needed to uniquely identify a certificate

        # Check for existing certificates
        if GeneralCertificates.objects.filter(event_id=event_id).exists():
            return Response(
                {'error': 'A certificate for this event already exists.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Use the super().post() to handle the normal create operation
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            print("Error:", e)
            response = Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return response
    
    
class GeneralCertificatesDetail(generics.RetrieveUpdateAPIView):
    queryset = GeneralCertificates.objects.all()
    serializer_class = GeneralCertificatesSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_update(serializer)
            print("Request:", request.data)
            print("Updated instance:", serializer.data)
            return Response(serializer.data)
        except Exception as e:
            print("Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
class GeneralCertificatesDeleteView(generics.DestroyAPIView):
    queryset = GeneralCertificates.objects.all()
    serializer_class = GeneralCertificatesSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)   
    
    
class GeneralEventUserToday(APIView):
    def get(self, request):
        current_date = timezone.now().date()

        # Correct field name for related model
        events = GeneralEvent.objects.filter(general_single_events__date=current_date).distinct()

        events_data = GeneralEventListSerializer(events, many=True).data

        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
class GeneralEventUserThisWeek(APIView):
    def get(self, request):
        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Use the correct related name for filtering
        events = GeneralEvent.objects.filter(general_single_events__date__range=[start_of_week, end_of_week]).distinct()
        events_data = GeneralEventListSerializer(events, many=True).data
        
        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
        
class GeneralEventThisMonthUser(APIView):
    def get(self, request):
        today = timezone.now().date()
        start_of_month = today.replace(day=1)
        
        # Calculate the end of the month
        end_of_month = start_of_month.replace(day=calendar.monthrange(start_of_month.year, start_of_month.month)[1])
        
        # Filter events for the current month
        events = GeneralEvent.objects.filter(
            general_single_events__date__gte=start_of_month,
            general_single_events__date__lt=end_of_month + timedelta(days=1)
        ).distinct()
        
        events_data = GeneralEventListSerializer(events, many=True).data
        
        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
        
class GeneralEventThisYearUser(APIView):
    def get(self, request):
        today = timezone.now().date()
        start_of_year = today.replace(month=1, day=1)
        end_of_year = today.replace(month=12, day=31)
        
        # Filter events for the current year only
        events = GeneralEvent.objects.filter(
            general_single_events__date__gte=start_of_year, 
            general_single_events__date__lte=end_of_year
        ).distinct()
        
        events_data = GeneralEventListSerializer(events, many=True).data
        
        return Response({
            'events': events_data,
        }, status=status.HTTP_200_OK)
        
from django.utils import timezone
from datetime import datetime, timedelta

class GeneralEventListbannerView(APIView):
    def calculate_end_date(self, event):
        """
        Calculates the start and end dates of the event based on its general single events.
        """
        single_events = event.general_single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def calculate_multi_event_times(self, event):
        """
        Calculates the starting time of the first MultiEvent and ending time of the last MultiEvent
        when days = 1 for the given general event.
        """
        single_event = event.general_single_events.filter(day=1).first()
        if single_event:
            multi_events = single_event.general_multi_events.all()
            if multi_events.exists():
                start_time = multi_events.first().starting_time
                end_time = multi_events.last().ending_time
                return start_time, end_time
        return None, None

    def get_event_status(self, event):
        """
        Determines the status of the event based on current datetime and multi-event times,
        with a 15-minute buffer for live status.
        """
        current_datetime = timezone.now()  # Get the current time
        start_date, end_date = self.calculate_end_date(event)
        start_time, end_time = self.calculate_multi_event_times(event)

        if start_date and end_date and start_time and end_time:
            # Combine date and time to get the full datetime for start and end
            event_start_datetime = timezone.make_aware(datetime.combine(start_date, start_time))
            event_end_datetime = timezone.make_aware(datetime.combine(end_date, end_time))

            # Adding the 15-minute buffer before the start and after the end
            live_start_datetime = event_start_datetime - timedelta(minutes=15)
            live_end_datetime = event_end_datetime + timedelta(minutes=15)

            # Determine event status based on the current time and the time buffers
            if current_datetime < live_start_datetime:
                return "Upcoming"  # Before 15 minutes of the first multi-event's start time
            elif live_start_datetime <= current_datetime <= live_end_datetime:
                return "Live"  # Within the 15 minutes before start and 15 minutes after the last end time
            elif current_datetime > live_end_datetime:
                return "Completed"  # After 15 minutes of the last multi-event's end time
        return "Upcoming"

    def get(self, request):
        """
        Retrieves all general events, categorizes them based on status, and returns serialized data.
        """
        events = GeneralEvent.objects.all()
        live_events_data = []
        upcoming_events_data = []
        completed_events_data = []

        for event in events:
            # Determine event status
            status = self.get_event_status(event)

            # Calculate start and end dates
            start_date, end_date = self.calculate_end_date(event)

            # Calculate start and end times of MultiEvent for days = 1
            start_time, end_time = self.calculate_multi_event_times(event)

            # Serialize event data
            event_data = GeneralEventBannerSerializer(event).data
            event_data['start_date'] = start_date
            event_data['end_date'] = end_date
            event_data['times'] = {
                'start_time': start_time,
                'end_time': end_time
            }

            # Append to appropriate list based on status
            if status == "Live":
                live_events_data.append(event_data)
            elif status == "Upcoming":
                upcoming_events_data.append(event_data)
            else:
                completed_events_data.append(event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })

        
class GeneralUploadAttachmentView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        file = request.FILES.get('file')
        single_event_id = request.data.get('single_event')

        if not file or not single_event_id:
            return Response({'error': 'File and Single Event are required'}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new Attachment instance
        attachment = GeneralAttachment.objects.create(single_event_id=single_event_id, file=file)

        serializer = GeneralAttachmentSerializer(attachment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class GeneralListAttachmentsView(generics.ListAPIView):
    queryset = GeneralAttachment.objects.all()
    serializer_class = GeneralAttachmentSerializer



class GeneralAttachmentDeleteAPIView(APIView):
    def delete(self, request, *args, **kwargs):
        try:
            attachment = GeneralAttachment.objects.get(id=kwargs['pk'])
        except GeneralAttachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
        
        attachment.delete()
        return Response({'message': 'Attachment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
    
    
class GeneralAttachmentUpdateAPIView(APIView):
    def put(self, request, *args, **kwargs):
        try:
            attachment = GeneralAttachment.objects.get(id=kwargs['pk'])
        except GeneralAttachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = GeneralAttachmentSerializer(attachment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class NewsletterListCreateView(generics.ListCreateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    
class NewsletterListView(generics.ListAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    
class NewsletterDeleteView(APIView):
    def delete(self, request, pk, format=None):
        try:
            newsletter = Newsletter.objects.get(pk=pk)
            newsletter.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Newsletter.DoesNotExist:
            return Response(
                {"detail": "Not found."},
                status=status.HTTP_404_NOT_FOUND
            )
            
class NewsletterUpdateView(generics.UpdateAPIView):
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    lookup_field = 'pk'

    def put(self, request, *args, **kwargs):
        print("Request data:", request.data)
        print("URL kwargs:", self.kwargs)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            print("Validation errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class GeneralAttachmentsBySingleEventView(generics.ListAPIView):
#     serializer_class = GeneralAttachmentSerializer

#     def get_queryset(self):
#         single_event_id = self.request.query_params.get('single_event')
#         if single_event_id:
#             queryset = GeneralAttachment.objects.filter(single_event=single_event_id)
#             print(f'GeneralAttachmentsBySingleEventView: Fetched {queryset.count()} attachments for single_event_id={single_event_id}')
#             for attachment in queryset:
#                 print(f'Attachment ID: {attachment.id}, File: {attachment.file}')
#             return queryset
#         print('GeneralAttachmentsBySingleEventView: No single_event_id provided')
#         return GeneralAttachment.objects.none()
    
    
    
class GeneralAssociateFileWithUserView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received request data:", request.data)   
        attachment_id = request.data.get('attachmentId')
        single_event_id = request.data.get('singleEventId')   

        if not attachment_id or not single_event_id:
            print("Missing attachmentId or singleEventId")   
            return Response({'error': 'attachmentId and singleEventId are required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            attachment =GeneralAttachment.objects.get(id=attachment_id)
            single_event = GeneralSingleEvent.objects.get(id=single_event_id)
        except GeneralAttachment.DoesNotExist:
            return Response({'error': 'Attachment not found'}, status=status.HTTP_404_NOT_FOUND)
        except GeneralSingleEvent.DoesNotExist:
            return Response({'error': 'SingleEvent not found'}, status=status.HTTP_404_NOT_FOUND)

        association, created = GeneralUserFileAssociation.objects.get_or_create(
            user=request.user,
            attachment=attachment
        )
        
        return Response({'message': 'File associated with user successfully'}, status=status.HTTP_200_OK)


from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from django.db import transaction
 

class CreatePodcast(APIView):
    def post(self, request):
        try:
            print("Request data:", request.data)
            with transaction.atomic():
                # Extract data from the request
                name = request.data.get('name')
                date = request.data.get('date')
                starting_time = request.data.get('starting_time')
                ending_time = request.data.get('ending_time')
                youtube_url = request.data.get('youtube_url')
                banner = request.FILES.get('banner')
                image = request.FILES.get('image')
                # Extract host and guest IDs manually
                host_ids = [value for key, value in request.data.items() if key.startswith('host')]
                guest_ids = [value for key, value in request.data.items() if key.startswith('guest')]

                # Create the podcast
                podcast = Podcastfcpipodcast.objects.create(
                    name=name,
                    date=date,
                    starting_time=starting_time,
                    ending_time=ending_time,
                    youtube_url=youtube_url,
                    banner=banner,
                    image = image 
                )
                # Fetch and set the ManyToMany relationships
                if host_ids:
                    hosts = Speaker.objects.filter(id__in=host_ids)
                    podcast.hosts.set(hosts)
                    print("Hosts set:", hosts)

                if guest_ids:
                    guests = Speaker.objects.filter(id__in=guest_ids)
                    podcast.guests.set(guests)
                    print("Guests set:", guests)
                
                print("Created podcast:", podcast)

        except Speaker.DoesNotExist as e:
            print("Speaker not found:", e)
            return Response({"error": "Speaker not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("Error:", e)
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({"message": "Podcast created successfully", "podcast_id": podcast.id}, status=status.HTTP_201_CREATED)

class PodcastListViewall(generics.ListAPIView):
    queryset = Podcastfcpipodcast.objects.all()  # Updated to get all podcasts
    serializer_class = PodcastSerializer
    
    
class PodcastDeleteView(generics.DestroyAPIView):
    queryset = Podcastfcpipodcast.objects.all()
    serializer_class = PodcastSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class PodcastUpdateView(APIView):
    def put(self, request, pk):
        try:
            podcast = Podcastfcpipodcast.objects.get(pk=pk)

            # Extract basic data
            name = request.data.get('name')
            date = request.data.get('date')
            starting_time = request.data.get('starting_time')
            ending_time = request.data.get('ending_time')
            youtube_url = request.data.get('youtube_url')
            banner = request.FILES.get('banner') 
            image = request.FILES.get('image') 
       
            host_ids = [value for key, value in request.data.items() if key.startswith('host')]
            guest_ids = [value for key, value in request.data.items() if key.startswith('guest')]

           
            data = {
                'name': name,
                'date': date,
                'starting_time': starting_time,
                'ending_time': ending_time,
                'youtube_url': youtube_url,
            }
            if banner:
                data['banner'] = banner

            if image:
                data['image'] = image
            serializer = PodcastUpdateSerializer(podcast, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()

          
                if host_ids:
                    hosts = Speaker.objects.filter(id__in=host_ids)
                    podcast.hosts.set(hosts)
                if guest_ids:
                    guests = Speaker.objects.filter(id__in=guest_ids)
                    podcast.guests.set(guests)

          
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Podcastfcpipodcast.DoesNotExist:
            return Response({"error": "Podcast not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





from django.utils import timezone
from datetime import datetime

from datetime import datetime
from django.utils import timezone

from datetime import timedelta
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response

class PodcastListView(APIView):
    def get_podcast_status(self, podcast):
        """
        Determines the status of the podcast based on the current datetime and podcast start/end times,
        considering a 15-minute buffer before the start time and after the end time.
        """
        current_datetime = timezone.now()  # Get current time
        podcast_start_datetime = timezone.make_aware(datetime.combine(podcast.date, podcast.starting_time))
        podcast_end_datetime = timezone.make_aware(datetime.combine(podcast.date, podcast.ending_time))

        # Calculate 15-minute buffer before the start time and after the end time
        live_start_datetime = podcast_start_datetime - timedelta(minutes=15)
        live_end_datetime = podcast_end_datetime + timedelta(minutes=15)

        # Debugging: Print current time and buffer intervals
        # print(f"Current Time: {current_datetime}")
        # print(f"Event Start Time: {podcast_start_datetime}")
        # print(f"Event End Time: {podcast_end_datetime}")
        # print(f"Fifteen Minutes Before Start: {live_start_datetime}")
        # print(f"Fifteen Minutes After End: {live_end_datetime}")

        # Determine status based on current time in relation to buffer windows
        if current_datetime < live_start_datetime:
            return "Upcoming"
        elif live_start_datetime <= current_datetime <= live_end_datetime:
            return "Live"
        elif current_datetime > live_end_datetime:
            return "Completed"
        else:
            return "Unknown"

    def get(self, request):
        """
        Retrieves all podcasts, categorizes them based on status, and returns serialized data.
        """
        podcasts = Podcastfcpipodcast.objects.all()
        live_podcasts_data = []
        upcoming_podcasts_data = []
        completed_podcasts_data = []

        for podcast in podcasts:
            # Determine podcast status
            status = self.get_podcast_status(podcast)

            # Serialize podcast data
            podcast_data = PodcastSerializer(podcast).data

            # Append to appropriate list based on status
            if status == "Live":
                live_podcasts_data.append(podcast_data)
            elif status == "Upcoming":
                upcoming_podcasts_data.append(podcast_data)
            elif status == "Completed":
                completed_podcasts_data.append(podcast_data)

        # Return response with categorized podcasts
        return Response({
            'live_podcasts': live_podcasts_data,
            'upcoming_podcasts': upcoming_podcasts_data,
            'completed_podcasts': completed_podcasts_data,
        })

        
import urllib.parse       
class PodcastDetailView(APIView):
    def get(self, request, name, *args, **kwargs):
        # Convert hyphens back to spaces
        decoded_name = name.replace('-', ' ')
        
        try:
           
            podcast = Podcastfcpipodcast.objects.get(name=decoded_name)
        except Podcastfcpipodcast.DoesNotExist:
            return Response({'error': 'Podcast not found'}, status=404)

        # Serialize the podcast data
        serializer = PodcastSerializer(podcast)
        
        return Response(serializer.data)
    
    
class TotalEventCountView(APIView):
 
 
    def get(self, request):
     
        event_count = Event.objects.count()
        general_event_count = GeneralEvent.objects.count()

        # Calculate the total count
        total_events = event_count + general_event_count

        # Return the response with the total event count
        return Response({
            'total_events': total_events,
            'event_count': event_count,
            'general_event_count': general_event_count
        })
        
        
        
class MemberCountAPIView(APIView):
    def get(self, request):
        member_count = Member.objects.count()
        return Response({'member_count': member_count})
    
    
    
class SpeakerCountAPIView(APIView):
    def get(self, request):
        speaker_count = Speaker.objects.count()
        return Response({'speaker_count': speaker_count})
    
class  NewsletterCountAPIView(APIView):
    def get(self, request):
        newsletter_count =  Newsletter.objects.count()
        return Response({'newsletter_count': newsletter_count})
    
class PodcastCountAPIView(APIView):
    def get(self, request):
        podcast_count = Podcastfcpipodcast.objects.count()
        return Response({'podcast_count': podcast_count})

class SingleEventAttachmentsView(generics.GenericAPIView):
    serializer_class = AttachmentSerializer

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        try:
            single_event = SingleEvent.objects.get(id=event_id)
        except SingleEvent.DoesNotExist:
            raise NotFound("SingleEvent not found")

        attachments = single_event.attachments.all()
        serializer = self.get_serializer(attachments, many=True)
        print("serializer.data attachments", serializer.data)
        return Response(serializer.data)

    
class GeneralSingleEventAttachmentsView(generics.GenericAPIView):
    serializer_class = GeneralAttachmentSerializer

    def get(self, request, *args, **kwargs):
        event_id = self.kwargs.get('event_id')
        try:
            general_single_event = GeneralSingleEvent.objects.get(id=event_id)
        except GeneralSingleEvent.DoesNotExist:
            raise NotFound("GeneralSingleEvent not found")

        attachments = general_single_event.general_attachments.all()
        serializer = self.get_serializer(attachments, many=True)
        print("serializer.data general_attachments", serializer.data)
        return Response(serializer.data)


