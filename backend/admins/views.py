from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminSerializer,ForumSerializer,SpeakerSerializer,EventSerializer ,SingleEventSerializer,EventListSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from.models import Forum,Speaker,Event,SingleEvent
from datetime import datetime, timedelta
from rest_framework.exceptions import APIException 
from rest_framework.exceptions import NotFound
 

 
 
 

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
    
 

class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            # Save the event object
            event = serializer.save()

            # Process selected speakers
            selected_speaker_ids = request.data.get('speakers', [])
            selected_speakers = Speaker.objects.filter(pk__in=selected_speaker_ids)
            event.speakers.set(selected_speakers)
 
            banner_file = request.data.get('banner')
            if banner_file:
                event.banner.save(banner_file.name, banner_file, save=True)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




        
        
class SingleEventListCreate(APIView):
    def post(self, request):
        data = request.data
        print("Received data:", data)

        forum_id = data.get('forum')
        event_name = data.get('event_name')
        event_date = data.get('date')
        starting_time = data.get('starting_time')
        ending_time = data.get('ending_time')
        speakers = data.get('speakers', [])
        days = int(data.get('days', 1))
        banner = request.FILES.get('banner')  

        print("Banner:", banner)
        print("Speakers:", speakers)

        try:
            event_date = datetime.strptime(event_date, '%Y-%m-%d').date()
            if starting_time is not None:
                starting_time = datetime.strptime(starting_time, '%H:%M').time()
            if ending_time is not None:
                ending_time = datetime.strptime(ending_time, '%H:%M').time()
        except ValueError as e:
            print('Invalid date or time format:', str(e))
            return Response({'error': 'Invalid date or time format. Please provide date in YYYY-MM-DD format and time in HH:MM format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            forum = Forum.objects.get(id=forum_id) 
        except Forum.DoesNotExist:
            print('Forum does not exist')
            raise NotFound(detail='Forum does not exist')

        print("Event Date (Parsed):", event_date)
        print("Forum:", forum)

        event = Event.objects.create(
            forum=forum,
            event_name=event_name,
            date=event_date,
            days=days,
            banner=banner,
        )
        event.speakers.set(speakers)

        single_events_created = []
        for schedule_data in data.get('schedules', []):
            schedule_data['date'] = event_date
            schedule_data['event'] = event.id   
            if starting_time is not None:
                schedule_data['starting_time'] = starting_time
            if ending_time is not None:
                schedule_data['ending_time'] = ending_time
            serializer = SingleEventSerializer(data=schedule_data)
            if serializer.is_valid():
                serializer.save()
                single_events_created.append(serializer.data)
            else:
                print("Serializer Errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        print("Single Events Created:", single_events_created)
        return Response(single_events_created, status=status.HTTP_201_CREATED)



    
    
class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventListSerializer(events, many=True)
        print(serializer.data)
        return Response(serializer.data)
    
    
class EditEventAPIView(APIView):
    def get(self, request, pk):
        try:
            event = Event.objects.prefetch_related('single_events').get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            event = Event.objects.get(pk=pk)
            serializer = EventSerializer(event, data=request.data)
            print(request.data)
            if serializer.is_valid():
                # Save the updated event data
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            # Return a 404 response if the event with the given pk does not exist
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log any unexpected errors for debugging
            print(e)
            return Response({'error': 'An unexpected error occurred'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



        
class EventDetailView(APIView):
    def get(self, request, pk):
        try:
            event = Event.objects.prefetch_related('single_events').get(pk=pk)
            serializer = EventSerializer(event)
            return Response(serializer.data)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

