from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminSerializer,ForumSerializer,SpeakerSerializer,EventSerializer ,SingleEventSerializer,EventListSerializer,EventSpeakerSerializer,MultiEventSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from.models import Forum,Speaker,Event,SingleEvent,MultiEvent
from datetime import datetime, timedelta
from rest_framework.exceptions import APIException 
from rest_framework.exceptions import NotFound
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
 
from django.db import transaction
import json

 

 
import logging 
 
 

class AdminLogin(APIView):
    def post(self, request):
        try:
            data = request.data
            email = data.get('email')
            password = data.get('password')
            if email is None or password is None:
                raise ValueError("Email and password must be provided")

            
            user = authenticate(request, email=email, password=password)
            if user is not None and user.is_staff and user.is_superuser:
              
                login(request, user)
                return Response({'status': 200, 'message': 'Admin login successful'})
            else:
                return Response({'status': 400, 'error': 'Invalid email or password'}, status=status.HTTP_400_BAD_REQUEST)
        except ValueError as e:
            return Response({'status': 400, 'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print("An error occurred:", e)
            return Response({'status': 500, 'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        return Response({'status': 405, 'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)



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

class EventListCreate(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            print("Request Data:", request.data)

            # Extract event data from request
            event_data = {
                'event_name': request.data.get('event_name'),
                'date': request.data.get('date'),
                'days': request.data.get('days'),
                'forum': request.data.get('forum'),
                'speakers': [speaker.strip('"') for speaker in request.data.getlist('speakers[]')],
                'banner': request.data.get('banner')
            }

            # Extract and deserialize single events data from request
            single_events_data = request.data.getlist('single_events[]')  # Use getlist to get all single events
            print("Event Data:", event_data)
            print("Single Events Data:", single_events_data)

            # Serialize event data
            event_serializer = EventSerializer(data=event_data)
            if event_serializer.is_valid():
                event = event_serializer.save()
            else:
                print("Event Serializer Errors:", event_serializer.errors)
                return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            # Process and save each single event data
            for single_event_data in single_events_data:
                single_serializer = SingleEventSerializer(data=json.loads(single_event_data))
                if single_serializer.is_valid():
                    single_instance = single_serializer.save(event=event)
                else:
                    print("Single Event Serializer Errors:", single_serializer.errors)
                    return Response(single_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                # Process and save multi event data for this single event
                multi_events_data = single_serializer.validated_data.get('multi_events', [])
                for multi_event_data in multi_events_data:
                    # Check if the multi event already exists
                    existing_multi_event = MultiEvent.objects.filter(
                        single_event=single_instance,
                        starting_time=multi_event_data['starting_time'],
                        ending_time=multi_event_data['ending_time']
                    ).first()
                    
                    if existing_multi_event:
                        print("Multi Event already exists:", existing_multi_event)
                    else:
                        multi_event_data['single_event'] = single_instance.id
                        multi_serializer = MultiEventSerializer(data=multi_event_data, context={'single_event': single_instance})
                        if multi_serializer.is_valid():
                            multi_serializer.save()
                        else:
                            print("Multi Event Serializer Errors:", multi_serializer.errors)
                            return Response(multi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return Response({'message': 'Event and associated data created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)














    
    
class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventListSerializer(events, many=True)
        print(serializer.data)
        return Response(serializer.data)
    
    
class EditEventAPIView(APIView):
    
    def put(self, request, pk):
        try:
           
            event = Event.objects.get(pk=pk)
            
           
            serializer = EventSerializer(event, data=request.data, partial=True)

            print(request.data)   
      
            if serializer.is_valid():
          
                serializer.save()
                print(serializer.data,'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')  
                
 
                return Response(serializer.data)
            else:
           
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
    
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
 
            print(e)
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




        
class EventDetailView(APIView):
    def get(self, request, pk):
        try:
            event = Event.objects.prefetch_related('single_events').get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            print('error')
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
            
 

class EventListView(APIView):
    def get_event_status(self, event):
        current_date = datetime.now().date()
        if event.date > current_date:
            return "Upcoming"
        elif event.date == current_date:
            return "Live"
        else:
            return "Completed"

    def get(self, request):
        
        events = Event.objects.all()

        live_events = []
        upcoming_events = []
        completed_events = []

        for event in events:
            status = self.get_event_status(event)
            if status == "Live":
                live_events.append(event)
            elif status == "Upcoming":
                upcoming_events.append(event)
            else:
                completed_events.append(event)

        live_events_data = EventListSerializer(live_events, many=True).data
        upcoming_events_data = EventListSerializer(upcoming_events, many=True).data
        completed_events_data = EventListSerializer(completed_events, many=True).data

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })

class SingleEventDetailView(APIView):
    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events'), pk=event_id)
            serializer = EventListSerializer(event)
            
            day = request.GET.get('day')  
            if day:
                # Filter single events for the specified day
                single_events = event.single_events.filter(day=day)  
                
                # Serialize the filtered single events
                serializer.data['single_events'] = EventListSerializer(single_events, many=True).data
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

         
            
class EventSpeakersView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        serializer = EventSpeakerSerializer(event)
        print("vvvvvvvvvvvvvvvvv",serializer.data)
        return Response(serializer.data)


