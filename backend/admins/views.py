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
from django.core.exceptions import ObjectDoesNotExist

 
 
 

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
        print("Request Data:", data)

        try:
            forum_id = data['forum']
            forum = Forum.objects.get(id=forum_id)
        except (KeyError, ObjectDoesNotExist):
            return Response({'error': 'Invalid forum ID'}, status=status.HTTP_400_BAD_REQUEST)

        event_serializer = EventSerializer(data=data)
        if event_serializer.is_valid():
            event = event_serializer.save(forum=forum)
        else:
            return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        single_events_data = data.get('schedules', [])
        print("mmmmmmmmmmmm:",single_event_data)
        for single_event_data in single_events_data:
            single_event_data['event'] = event.id
            serializer = SingleEventSerializer(data=single_event_data)
            if serializer.is_valid():
                serializer.save()
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            # Print single event data inside the loop
            print("Single Event Data:", single_event_data)

        # Associate speakers with the event
        speakers_ids = data.get('speakers', [])
        event.speakers.add(*speakers_ids)

        print("Response Data:", {'message': 'Event and single events created successfully'})
        return Response({'message': 'Event and single events created successfully'}, status=status.HTTP_201_CREATED)




    
    
class EventListView(APIView):
    def get(self, request):
        events = Event.objects.all()
        serializer = EventListSerializer(events, many=True)
        print(serializer.data)
        return Response(serializer.data)
    
    
class EditEventAPIView(APIView):
    
    def put(self, request, pk):
        try:
            # Retrieve the event instance by its primary key
            event = Event.objects.get(pk=pk)
            
            # Create a serializer instance with the retrieved event and request data,
            # allowing partial updates
            serializer = EventSerializer(event, data=request.data, partial=True)

            print(request.data)  # Print the request data for debugging
            
            # Validate the serializer
            if serializer.is_valid():
                # Save the serializer data (update the event)
                serializer.save()
                print(serializer.data,'wwwwwwwwwwwwwwwwwwwwwwwwwwwwwww')  # Print the updated data for debugging
                
                # Return the updated data
                return Response(serializer.data)
            else:
                # If the serializer is not valid, return validation errors
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Event.DoesNotExist:
            # If the event with the given primary key does not exist, return a 404 error
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # Log any unexpected errors for debugging and return a 500 error
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

