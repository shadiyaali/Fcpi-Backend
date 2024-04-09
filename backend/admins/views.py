from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminSerializer,ForumSerializer,SpeakerSerializer,EventSerializer ,SingleEventSerializer,EventListSerializer,EventSpeakerSerializer,MultiEventSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from.models import Forum,Speaker,Event,SingleEvent
from datetime import datetime, timedelta
from rest_framework.exceptions import APIException 
from rest_framework.exceptions import NotFound
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
 
 
 

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
    
 
 
 
 
from django.db import transaction
 

class EventListCreate(APIView):
    @transaction.atomic
    def post(self, request):
     
        event_data = {
            'event_name': request.data.get('event_name'),
            'date': request.data.get('date'),
            'days': request.data.get('days'),
            'forum': request.data.get('forum'),
            'speakers': request.data.getlist('speakers[]'),
            'banner': request.data.get('banner')
        }
        single_events_data = request.data.getlist('single_events[]')  
        
        multi_events_data = request.data.getlist('multi_events[]')
        print("Received event_data:", event_data)
        print("Received single_events_data:", single_events_data)
        print("Received multi_events_data:", multi_events_data)
        
        event_serializer = EventSerializer(data=event_data)
        
        
        if event_serializer.is_valid():
            event = event_serializer.save()
        else:
            return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
        for single_data in single_events_data:
            single_data['event'] = event.id
            single_serializer = SingleEventSerializer(data=single_data)
            if single_serializer.is_valid():
                single_serializer.save()
            else:
                print(single_serializer.errors)
                return Response(single_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Create MultiEvent instances
        for multi_data in multi_events_data:
            multi_data['event'] = event.id
            multi_serializer = MultiEventSerializer(data=multi_data)
            if multi_serializer.is_valid():
                multi_serializer.save()
            else:
                print(multi_serializer.errors)
                return Response(multi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Event and associated data created successfully'}, status=status.HTTP_201_CREATED)






    
    
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

        live_events_data = EventSerializer(live_events, many=True).data
        upcoming_events_data = EventSerializer(upcoming_events, many=True).data
        completed_events_data = EventSerializer(completed_events, many=True).data

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })

class SingleEventDetailView(APIView):
    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events'), pk=event_id)
            serializer = EventSerializer(event)
            
            day = request.GET.get('day')  
            if day:
                single_events = event.single_events.filter(day=day)  
                serializer.data['single_events'] = EventSerializer(single_events, many=True).data
                
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
         
            
class EventSpeakersView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        serializer = EventSpeakerSerializer(event)
        print("vvvvvvvvvvvvvvvvv",serializer.data)
        return Response(serializer.data)