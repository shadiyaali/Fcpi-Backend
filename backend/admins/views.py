from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminSerializer,ForumSerializer,SpeakerSerializer,CertificatesListSerializer,EventSerializer,BlogsSerializerFoum,CertificatesSerializer,BlogsSerializer,BlogsContentsSerializer,SingleEventSerializer,ForumMemberSerializer,MemeberSerializer,EventListSerializer,EventSpeakerSerializer,MultiEventSerializer,RetrieveSingleEventSerializer,EventBannerSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from.models import Forum,Speaker,Event,SingleEvent,MultiEvent,Member,ForumMember,BlogsContents,Blogs,Certificates
from datetime import datetime, timedelta
from rest_framework.exceptions import APIException 
from rest_framework.exceptions import NotFound
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db import transaction
import json
from django.db import transaction 
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

            event_serializer = EventSerializer(data=event_data)
            if event_serializer.is_valid():
                event = event_serializer.save()
            else:
                print("Event Serializer Errors:", event_serializer.errors)
                return Response(event_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            single_events_data = request.data.getlist('single_events[]')
            print("Event Data:", event_data)
            print("Single Events Data:", single_events_data)

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
            
 

 


from datetime import datetime, timedelta

from datetime import datetime

from datetime import datetime
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Event
from .serializers import EventListSerializer

class EventListView(APIView):
    def calculate_end_date(self, event):
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def get_event_status(self, event):
        current_date = datetime.now().date()
        start_date, end_date = self.calculate_end_date(event)
        if start_date and end_date:
            if start_date <= current_date <= end_date:
                return "Live"
            elif current_date > end_date:
                return "Completed"
        return "Upcoming"

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

        for event in live_events:
            start_date, end_date = self.calculate_end_date(event)
            live_event_data = EventListSerializer(event).data
            live_event_data['start_date'] = start_date
            live_event_data['end_date'] = end_date
            live_events_data.append(live_event_data)

        for event in upcoming_events:
            start_date, end_date = self.calculate_end_date(event)
            upcoming_event_data = EventListSerializer(event).data
            upcoming_event_data['start_date'] = start_date
            upcoming_event_data['end_date'] = end_date
            upcoming_events_data.append(upcoming_event_data)

        for event in completed_events:
            start_date, end_date = self.calculate_end_date(event)
            completed_event_data = EventListSerializer(event).data
            completed_event_data['start_date'] = start_date
            completed_event_data['end_date'] = end_date
            completed_events_data.append(completed_event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })



 
 
 
class SingleEventDetailView(APIView):
    def calculate_end_date(self, start_date, end_date):
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        return end_date.strftime('%Y-%m-%d')

    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events__multi_events'), pk=event_id)
            serialized_data = EventListSerializer(event, context={'request': request}).data
            print(serialized_data)

            serialized_single_events = []
            single_events = event.single_events.all().order_by('day')
            if single_events.exists():  # Check if any single events exist
                for single_event in single_events:  
                    single_event_dict = RetrieveSingleEventSerializer(single_event).data
                    single_event_dict['day'] = single_event.day  
                    serialized_multi_events = []
                    for multi_event in single_event.multi_events.all():
                        serialized_multi_event = MultiEventSerializer(multi_event).data
                        serialized_multi_events.append(serialized_multi_event)
                    single_event_dict['multi_events'] = serialized_multi_events
                    serialized_single_events.append(single_event_dict)

                # Get start and end dates if single events exist
                start_date = single_events.first().date.strftime('%Y-%m-%d')
                end_date = single_events.last().date.strftime('%Y-%m-%d')
            else:
                start_date = None
                end_date = None

            serialized_data['start_date'] = start_date
            serialized_data['end_date'] = end_date
            
            serialized_data['single_events'] = serialized_single_events
            return Response(serialized_data)

        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)



 

from django.utils import timezone

class SingleDetailView(APIView):
    def get(self, request, event_id):
        try:
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events'), pk=event_id)
            serialized_data = EventListSerializer(event, context={'request': request}).data
            
            serialized_single_events = []
            current_date = timezone.now().date()  # Get current date
            
            for index, single_event in enumerate(event.single_events.all(), start=1):
                serialized_single_event = SingleEventSerializer(single_event).data
                serialized_single_event['day'] = index  
                serialized_single_event['date'] = single_event.date.strftime('%Y-%m-%d')
                
                # Check if the event is live or completed
                if single_event.date <= current_date:
                    serialized_single_event['is_live_or_completed'] = True
                else:
                    serialized_single_event['is_live_or_completed'] = False
                
                serialized_single_events.append(serialized_single_event)
            
            serialized_data['single_events'] = serialized_single_events
            
            return Response(serialized_data)
               
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)

     
            
class EventSpeakersView(APIView):
    def get(self, request, event_id):
        event = get_object_or_404(Event, pk=event_id)
        serializer = EventSpeakerSerializer(event)
        print("vvvvvvvvvvvvvvvvv",serializer.data)
        return Response(serializer.data)


class EventListbannerView(APIView):
    def calculate_end_date(self, event):
        single_events = event.single_events.all()
        if single_events.exists():
            start_date = single_events.first().date
            end_date = single_events.last().date
            return start_date, end_date
        return None, None

    def get_event_status(self, event):
        current_date = datetime.now().date()
        start_date, end_date = self.calculate_end_date(event)
        if start_date and end_date:
            if start_date <= current_date <= end_date:
                return "Live"
            elif current_date > end_date:
                return "Past"
        return "Upcoming"

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

        for event in live_events:
            start_date, end_date = self.calculate_end_date(event)
            live_event_data = EventBannerSerializer(event).data
            live_event_data['start_date'] = start_date
            live_event_data['end_date'] = end_date
            live_events_data.append(live_event_data)

        for event in upcoming_events:
            start_date, end_date = self.calculate_end_date(event)
            upcoming_event_data = EventBannerSerializer(event).data
            upcoming_event_data['start_date'] = start_date
            upcoming_event_data['end_date'] = end_date
            upcoming_events_data.append(upcoming_event_data)

        for event in completed_events:
            start_date, end_date = self.calculate_end_date(event)
            completed_event_data = EventBannerSerializer(event).data
            completed_event_data['start_date'] = start_date
            completed_event_data['end_date'] = end_date
            completed_events_data.append(completed_event_data)

        return Response({
            'live_events': live_events_data,
            'upcoming_events': upcoming_events_data,
            'completed_events': completed_events_data,
        })



class MemberListCreate(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemeberSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

class MemberUpdateView(generics.UpdateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemeberSerializer

    def update(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        response = super().update(request, *args, **kwargs)
        print("Response Data:", response.data)
        return response 

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

        # Check if a forum member already exists for the given forum
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
 
 
 

 
class ForumMemberView(APIView):
    def put(self, request, forum_id, format=None):
        try:
            forum_member = ForumMember.objects.get(forum_id=forum_id)
        except ForumMember.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        selected_members = request.data.get('members', [])
        deleted_members = request.data.get('deleted_members', [])
        print("kkkkk", selected_members)
        print("DDDDD", deleted_members)
        
        # Add new members
        if selected_members:
            forum_member.member.add(*selected_members)

        # Remove deleted members
        if deleted_members:
            forum_member.member.remove(*deleted_members)

        # Add previously deleted members back to the forum if re-added
        for member_id in deleted_members:
            if member_id in selected_members:
                forum_member.member.add(member_id)

        serializer = ForumMemberSerializer(forum_member)
        print("ssssss", serializer.data)
        return Response(serializer.data)




 



class CreateBlog(APIView):
    def post(self, request):
        try:
            with transaction.atomic():
                forum_id = request.POST.get('forum')
                title = request.POST.get('title')
                author = request.POST.get('author')
                qualification = request.POST.get('qualification')
                date = request.POST.get('date')
                
                blog, created = Blogs.objects.get_or_create(
                    forum_id=forum_id,
                    title=title,
                    author=author,
                    qualification=qualification,
                    date=date
                )
                
                processed_contents = set()   
                for key, value in request.POST.items():
                    if key.startswith('blog_contents'):
                        index = key.split('[')[1].split(']')[0]
                        topic = request.POST.get(f'blog_contents[{index}][topic]')
                        description = request.POST.get(f'blog_contents[{index}][description]')
                        image = request.FILES.get(f'blog_contents[{index}][image]')
                        
                        content_key = (topic, description)   
                        if content_key in processed_contents:
                            continue   
                        processed_contents.add(content_key)
                        
                        if image:
                            image_name = image.name
                            content = BlogsContents.objects.create(
                                blog=blog,
                                topic=topic,
                                description=description,
                                image=image  
                            )
                        else:
                            content = BlogsContents.objects.create(
                                blog=blog,
                                topic=topic,
                                description=description,
                            )
                    
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(status=status.HTTP_201_CREATED)


class BlogListView(generics.ListAPIView):
    queryset = Blogs.objects.prefetch_related('blog_contents').all()
    serializer_class = BlogsSerializer
    
class BlogDeleteView(generics.DestroyAPIView):
    queryset = Blogs.objects.all()
    serializer_class = BlogsSerializer

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)



 
 
from rest_framework.generics import UpdateAPIView
class BlogUpdateView(UpdateAPIView):
    queryset = Blogs.objects.all()
    serializer_class = BlogsSerializerFoum

    def put(self, request, *args, **kwargs):
        print("request",request.data)
        try:
            blog = self.get_object()
            serializer = self.get_serializer(blog, data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
          
            if 'blog_contents' in request.data:
                blog_contents_data = request.data['blog_contents']
                for content_data in blog_contents_data:
                    content_id = content_data.get('id')
                    if content_id:
                       
                        content = blog.blog_contents.get(id=content_id)
                        content.topic = content_data.get('topic', content.topic)
                        content.description = content_data.get('description', content.description)
                        content.image = content_data.get('image', content.image)
                        content.save()
            print("serializer.data",serializer.data)
            return Response(serializer.data)
        except ValidationError as e:
            return Response({'error': 'Validation failed'}, status=status.HTTP_400_BAD_REQUEST)
        except Blogs.DoesNotExist:
            return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
 
        
        
        
        
class certificatesCreate(generics.ListCreateAPIView):
    queryset = Certificates.objects.all()
    serializer_class = CertificatesSerializer
    parser_classes = (MultiPartParser, FormParser)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        print("Request Data:", request.data)
        try:
            response = super().post(request, *args, **kwargs)
        except Exception as e:
            print("Error:", e)
            response = Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return response
        
class CertificatesList(generics.ListAPIView):
    queryset = Certificates.objects.all()
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
 
        
        
        
        
        
        
        
        
        
        


















