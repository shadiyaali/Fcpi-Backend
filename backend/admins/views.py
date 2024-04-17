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

 
from django.http import JsonResponse
 

from datetime import datetime, timedelta

 

class EventListCreate(APIView):
    @transaction.atomic
    def post(self, request):
        try:
            print("Request Data:", request.data)

            # Extract event data from request
            event_data = {
                'event_name': request.data.get('event_name'),
                'date': datetime.strptime(request.data.get('date'), '%d-%m-%Y').strftime('%Y-%m-%d'),  
                'days': int(request.data.get('days')),  
                'forum': request.data.get('forum'),
                'speakers': [speaker.strip('"') for speaker in request.data.getlist('speakers[]')],
                'banner': request.data.get('banner')
            }
            
            
            start_date = datetime.strptime(event_data['date'], '%Y-%m-%d')  
            dates = [start_date + timedelta(days=i) for i in range(event_data['days'])]

            event_serializer = EventSerializer(data=event_data)
            if event_serializer.is_valid():
                event = event_serializer.save()
            else:
                print("Event Serializer Errors:", event_serializer.errors)
                return JsonResponse(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            single_events_data = request.data.getlist('single_events[]')
            print("Event Data:", event_data)
            print("Single Events Data:", single_events_data)

            for single_event_data, date in zip(single_events_data, dates):
                single_event_data_dict = json.loads(single_event_data)
                single_event_data_dict['date'] = date.strftime('%d-%m-%Y')    
                single_event_data_dict['day'] = dates.index(date) + 1  # Assign day number
                single_serializer = SingleEventSerializer(data=single_event_data_dict)
                if single_serializer.is_valid():
                    single_instance = single_serializer.save(event=event)
                else:
                    print("Single Event Serializer Errors:", single_serializer.errors)
                    return JsonResponse(single_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                multi_events_data = single_serializer.validated_data.get('multi_events', [])
                for multi_event_data in multi_events_data:
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
                            return JsonResponse(multi_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'message': 'Event and associated data created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print("Error:", e)
            return JsonResponse({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





    
    
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

    def calculate_end_date(self, start_date, days):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
       
        end_date = start_date + timedelta(days=int(days) - 1)
        return end_date.strftime('%d-%m-%Y')

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

        live_events_data = []
        upcoming_events_data = []
        completed_events_data = []

        # Serialize and categorize events
        for event in live_events:
            live_event_data = EventListSerializer(event).data
            live_event_data['end_date'] = self.calculate_end_date(live_event_data['date'], live_event_data['days'])
            live_events_data.append(live_event_data)
        for event in upcoming_events:
            upcoming_event_data = EventListSerializer(event).data
            upcoming_event_data['end_date'] = self.calculate_end_date(upcoming_event_data['date'], upcoming_event_data['days'])
            upcoming_events_data.append(upcoming_event_data)
        for event in completed_events:
            completed_event_data = EventListSerializer(event).data
            completed_event_data['end_date'] = self.calculate_end_date(completed_event_data['date'], completed_event_data['days'])
            completed_events_data.append(completed_event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })



class SingleEventDetailView(APIView):
    def calculate_end_date(self, start_date, days):
       print("Calculating end date...")  # Add this line for debugging
       start_date = datetime.strptime(start_date, '%Y-%m-%d')
       end_date = start_date + timedelta(days=int(days) - 1)
       print("End Date:", end_date)  # Add this line for debugging
       return end_date.strftime('%d-%m-%Y')


    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events'), pk=event_id)
            day = request.GET.get('day')

            if day is not None:
                single_events = event.single_events.filter(day=day)
                serialized_data = EventListSerializer(event, context={'request': request}).data
                serialized_single_events = []

                for single_event in single_events:
                    serialized_single_event = SingleEventSerializer(single_event).data
                    serialized_single_event['end_date'] = self.calculate_end_date(single_event.start_date, single_event.duration)
                    serialized_single_events.append(serialized_single_event)

                serialized_data['single_events'] = serialized_single_events
                print("Serialized Data:", serialized_data)  # Add this line for debugging
                return Response(serialized_data)

            else:
                serialized_data = EventListSerializer(event, context={'request': request}).data
                return Response(serialized_data)

        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)




from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta
from .models import Event
from .serializers import EventListSerializer, SingleEventSerializer

class SingleDetailView(APIView):
    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events'), pk=event_id)
            serialized_data = EventListSerializer(event, context={'request': request}).data
            
            # Serialize single events with end date
            serialized_single_events = []
            for single_event in event.single_events.all():
                serialized_single_event = SingleEventSerializer(single_event).data
                serialized_single_event['end_date'] = self.calculate_end_date(single_event.start_date, single_event.duration)
                serialized_single_events.append(serialized_single_event)
            
            serialized_data['single_events'] = serialized_single_events
            
            return Response(serialized_data)
               
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def calculate_end_date(self, start_date, duration):
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = start_date_obj + timedelta(days=duration)
        
        return end_date_obj.strftime('%Y-%m-%d')

       
    
     
            
class EventSpeakersView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        serializer = EventSpeakerSerializer(event)
        print("vvvvvvvvvvvvvvvvv",serializer.data)
        return Response(serializer.data)


