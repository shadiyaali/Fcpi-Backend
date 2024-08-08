from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AdminSerializer,ForumSerializer, GalleryUpdateSerializer,AttachmentSerializerss,SingleAllEventSerializer,AttachmentSerializer,EventSerializerss,SingleEventSerializerss,GallerySerializer,BlogSerializer,GalleryImageSerializer,BoardSerializer,SpeakerSerializer,BoardMemberSerializer,EventSingleSerializer,CertificatesListSerializer,BannerSerializer,NewsSerializer,BlogsFormSerializer,EventSerializer,CertificatesSerializer,BlogsSerializer,BlogsContentsSerializer,SingleEventSerializer,ForumMemberSerializer,MemeberSerializer,EventListSerializer,EventSpeakerSerializer,MultiEventSerializer,RetrieveSingleEventSerializer,EventBannerSerializer
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from.models import Forum,Speaker,Event,SingleEvent,Gallery,Attachment,UserFileAssociation,MultiEvent,Member,ForumMember,BlogsContents,Blogs,Certificates,Banner,News,BoardMember,Board
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
 
        return Response(serializer.data)
    
    
 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import Event, SingleEvent, MultiEvent, Forum, Speaker
import json

class EventUpdateAPIView(APIView):
    def put(self, request, *args, **kwargs):
        print("Received data:", request.data)  # Print the entire request data
        
        event_id = kwargs.get('event_id')
        print("Event ID:", event_id)
        
        try:
            event = Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            return Response({'error': 'Event not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update Event fields
        event.event_name = request.data.get('event_name')
        event.date = request.data.get('date')
        event.days = request.data.get('days')
        event.forum = get_object_or_404(Forum, id=request.data.get('forum'))
        
        print("Updated event fields:", {
            "event_name": event.event_name,
            "date": event.date,
            "days": event.days,
            "forum": event.forum
        })
        
        if 'banner' in request.FILES:
            event.banner = request.FILES['banner']
        
        event.speakers.set(Speaker.objects.filter(id__in=request.data.getlist('speakers')))
        print("Updated speakers:", event.speakers.all())
        
        try:
            highlights = json.loads(request.data.get('highlights', '[]'))
            multi_events_data = json.loads(request.data.get('multi_events', '[]'))
            
            print("Highlights:", highlights)
            print("Multi Events Data:", multi_events_data)
            
            event.youtube_link = request.data.get('youtube_link')
            event.points = request.data.get('points')
            
            event.save()
            print("Event saved:", event)
            
            # Update or create SingleEvent instances
            single_event_data = {
                'event': event,
                'youtube_link': request.data.get('youtube_link'),
                'points': request.data.get('points'),
                'highlights': highlights,
                'date': request.data.get('date'),
                'day': request.data.get('days'),
            }

            single_event, created = SingleEvent.objects.update_or_create(
                event=event, defaults=single_event_data)
            print("SingleEvent saved:", single_event)
            
            # Delete existing MultiEvent instances
            MultiEvent.objects.filter(single_event=single_event).delete()
            
            # Create new MultiEvent instances
            for multi_event_data in multi_events_data:
                print("Processing multi event data:", multi_event_data)
                
                # Get the Speaker instance for single_speaker
                single_speaker = get_object_or_404(Speaker, id=multi_event_data.get('single_speaker'))
                
                multi_event = MultiEvent.objects.create(
                    single_event=single_event,
                    starting_time=multi_event_data.get('starting_time'),
                    ending_time=multi_event_data.get('ending_time'),
                    topics=multi_event_data.get('topics'),
                    single_speaker=single_speaker
                )
                
                print("MultiEvent saved:", multi_event)
        
        except json.JSONDecodeError:
            return Response({'error': 'Invalid JSON data'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Event updated successfully'}, status=status.HTTP_200_OK)











        
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
        Determines the status of the event based on current date and event dates.
        """
        current_date = datetime.now().date()
        start_date, end_date = self.calculate_end_date(event)
        if start_date and end_date:
            if current_date <= end_date:
                return "Live" if current_date >= start_date else "Upcoming"
            else:
                return "Completed"
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
            event = get_object_or_404(Event.objects.prefetch_related('speakers', 'single_events'), slug=slug)
            serialized_data = EventListSerializer(event, context={'request': request}).data
            
            serialized_single_events = []
            current_date = timezone.now().date()  # Get current date

            # Sort single_events by date before processing
            sorted_single_events = sorted(event.single_events.all(), key=lambda se: se.date)
            
            for index, single_event in enumerate(sorted_single_events, start=1):
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
    def get(self, request, slug):
        event = get_object_or_404(Event, slug=slug)
        serializer = EventSpeakerSerializer(event)
       
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



class BlogListView(APIView):
    def get(self, request):
        blogs = Blogs.objects.all()
        serializer = BlogSerializer(blogs, many=True)
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



 
 
 

 
# views.py

from rest_framework.parsers import MultiPartParser, FormParser
class BlogUpdateView(UpdateAPIView):
    queryset = Blogs.objects.all()
    serializer_class = BlogsFormSerializer
    parser_classes = (MultiPartParser, FormParser)

    def put(self, request, *args, **kwargs):
        print("Request data:", request.data)
        
        # Extract and format blog_contents data
        blog_contents_data = []
        for key, value in request.data.items():
            if key.startswith('blog_contents'):
                parts = key.split('[')
                index = int(parts[1][:-1])
                field = parts[2][:-1]

                while len(blog_contents_data) <= index:
                    blog_contents_data.append({})

                blog_contents_data[index][field] = value[0] if isinstance(value, list) else value

        # Create a new data dictionary to pass to the serializer
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

        # Preserve existing images if no new images are provided
        blog = self.get_object()
        if not data['blog_banner']:
            data['blog_banner'] = blog.blog_banner
        if not data['author_profile']:
            data['author_profile'] = blog.author_profile
        
        for index, content in enumerate(data['blog_contents']):
            if not content.get('image'):
                existing_content = blog.blog_contents.filter(id=content.get('id')).first()
                if existing_content:
                    content['image'] = existing_content.image

        print("Formatted data:", data)

        try:
            serializer = self.get_serializer(blog, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            print("Updated data:", serializer.data)
            return Response(serializer.data)
        except Exception as e:
            print("Error:", e)
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


        
        
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
    def put(self, request, board_id, format=None):  # Corrected parameter name to board_id
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
        all_members = set()
        board_members = BoardMember.objects.prefetch_related('member').all()

        for board_member in board_members:
            all_members.update(board_member.member.all())

        unique_members_list = list(all_members)
        
        serializer = MemeberSerializer(unique_members_list, many=True)
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
                'currentResearch': member.current_research,
                'conference': member.conference,
                'additionalInformation': member.additional_information,
                'achievements': member.achievements,
                'areasOfInterest': member.areas,
            }
        
            return JsonResponse(data)
        except Member.DoesNotExist:
            return JsonResponse({'error': 'Member not found'}, status=404)


class EventForumListView(APIView):
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
            if current_date <= end_date:
                return "Live" if current_date >= start_date else "Upcoming"
            else:
                return "Completed"
        return "Upcoming"

    def get(self, request, slug):
        forum = get_object_or_404(Forum, slug=slug)
    
        events = Event.objects.filter(forum=forum)

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

from rest_framework.generics import RetrieveAPIView
class AttachmentsBySingleEventView(generics.ListAPIView):
    serializer_class = AttachmentSerializer

    def get_queryset(self):
        single_event_id = self.request.query_params.get('single_event')
        if single_event_id:
            return Attachment.objects.filter(single_event=single_event_id)
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