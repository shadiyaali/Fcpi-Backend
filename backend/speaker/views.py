from django.shortcuts import render
from django.contrib.auth import authenticate, login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status 
from django.http import JsonResponse
from django.contrib.auth.hashers import check_password
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import Message,User
from .serializers import MessageSerializer
from rest_framework.generics import ListAPIView
from rest_framework.authentication import TokenAuthentication
from .models import Message
from admins.models import Forum,Event
from .serializers import MessageSerializer
from .models import SecondUser 
from django.contrib.auth import get_user_model
from .models import Message,GeneralMessage,GeneralEvent
from .serializers import MessageSerializer,MessageSerializerChat,SecondUserSerializer,GeneralMessageSerializer ,MessageSerializersChat,GeneralMessageSerializersChat
from django.shortcuts import get_object_or_404
User = get_user_model()

 
from accounts.models import User


class SecondUserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = SecondUser.objects.get(username=username)
            print("Username:", username)
            print("Password:", password)
            print("User Status:", user.status)

             
            if user.status == 'Active':
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User account is inactive'}, status=status.HTTP_400_BAD_REQUEST)
            
        except SecondUser.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)



class SecondUserCreateView(APIView):
    def post(self, request, *args, **kwargs):
        
        serializer = SecondUserSerializer(data=request.data)
        
       
        if serializer.is_valid():
            
            serializer.save()
            print(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SecondUserListView(APIView):
    def get(self, request, *args, **kwargs):
        second_users = SecondUser.objects.all()
        serializer = SecondUserSerializer(second_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class SecondUserStatusChangeView(APIView):
    def patch(self, request, pk, *args, **kwargs):
        try:
            user = SecondUser.objects.get(pk=pk)
            new_status = request.data.get('status')
            if new_status not in ['Active', 'Inactive']:
                return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.status = new_status
            user.save()
            serializer = SecondUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SecondUser.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        

 
 
from datetime import date

 
 
class MessageListView(APIView):
    def get(self, request, event_name=None, forum_name=None, format=None):
        current_date = date.today()

        # Debug prints for event_name and forum_name
        print(f"Event Name: {event_name}")
        print(f"Forum Name: {forum_name}")

        # Build the queryset based on the provided filters
        if event_name and forum_name:
            messages = Message.objects.select_related('event', 'forum', 'author__userprofile').filter(
                event__event_name=event_name,
                forum__title=forum_name,
                timestamp__date=current_date
            )
        elif event_name:
            messages = Message.objects.select_related('event', 'forum', 'author__userprofile').filter(
                event__event_name=event_name,
                timestamp__date=current_date
            )
        elif forum_name:
            print("Fetching messages with forum")
            messages = Message.objects.select_related('event', 'forum', 'author__userprofile').filter(
                forum__title=forum_name,
                timestamp__date=current_date
            )
        else:
            messages = Message.objects.select_related('event', 'forum', 'author__userprofile').filter(
                timestamp__date=current_date
            )

        # Log the queryset data
        for message in messages:
            print(f"Message ID: {message.id}, Event Name: {message.event.event_name if message.event else 'None'}, Forum Name: {message.forum.title if message.forum else 'None'}")

        # Serialize the data
        serializer = MessageSerializersChat(messages, many=True)
        data = serializer.data
        
        # Debug print for serialized data
        print("Serialized Data:", data)
        
        return JsonResponse(data, safe=False)


        
 
 
 
class SendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        print("Received data:", request.data)
        content = request.data.get('content')
        event_name = request.data.get('event_name')
        forum_name = request.data.get('forum_name')

        if content:
            try:
                author = request.user  # Fetch the author from the authenticated user
                print("Author found:", author)

                event = None
                if event_name:
                    event = Event.objects.get(event_name=event_name)

                forum = None
                if forum_name:
                    forum = Forum.objects.get(title=forum_name)

                message = Message.objects.create(
                    content=content,
                    author=author,
                    event=event,
                    forum=forum
                )

                serializer = MessageSerializer(message)
               
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Event.DoesNotExist:
                print("Invalid event name:", event_name)
                return Response({'error': 'Invalid event name'}, status=status.HTTP_400_BAD_REQUEST)
            except Forum.DoesNotExist:
                print("Invalid forum name:", forum_name)
                return Response({'error': 'Invalid forum name'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                print("General error:", str(e))
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            print("Missing content")
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)



        
        
class MessageUpdateView(APIView):
    def put(self, request, pk):
        try:
            message = Message.objects.get(pk=pk)
        except Message.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Toggle the 'answered' field
        message.answered = not message.answered
        message.save()

        serializer = MessageSerializer(message)
        return Response(serializer.data)


class ToggleUserStatus(APIView):
    def patch(self, request, user_id):
        try:
            user = SecondUser.objects.get(pk=user_id)
            old_status = user.status
            user.status = 'Active' if user.status == 'Inactive' else 'Inactive'
            user.save()

            

            serializer = SecondUserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except SecondUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class DeleteUser(APIView):
    def delete(self, request, user_id):
        try:
            user = SecondUser.objects.get(pk=user_id)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except SecondUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND) 
        
        
class DeactivateUserView(APIView):
    def post(self, request, user_id):
        try:
            user = SecondUser.objects.get(pk=user_id)
            user.status = 'Inactive'
            user.save()

            # Invalidate user's session
            logout(request)

            return Response({'message': 'User deactivated successfully'}, status=status.HTTP_200_OK)
        except SecondUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
 
from django.utils import timezone
class UserMessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        # Get messages only from the current day using `timestamp`
        today = timezone.now().date()
        messages = Message.objects.filter(author=user, timestamp__date=today)
        serializer = MessageSerializersChat(messages, many=True)
        data = serializer.data
        # print("User messages", data)  # Debugging output

        return JsonResponse(data, safe=False)


class GeneralUserMessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        # Get messages only from the current day using `timestamp`
        today = timezone.now().date()
        messages = GeneralMessage.objects.filter(author=user, timestamp__date=today)
        serializer = GeneralMessageSerializersChat(messages, many=True)
        data = serializer.data
        # print("General messages", data)  # Debugging output

        return JsonResponse(data, safe=False)


    
    
class GeneralSendMessageAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
      
        content = request.data.get('content')
        event_name = request.data.get('event_name')
      

        if content:
            try:
                author = request.user  # Fetch the author from the authenticated user
            

                event = None
                if event_name:
                    event = GeneralEvent.objects.get(event_name=event_name)

            

                message = GeneralMessage.objects.create(
                    content=content,
                    author=author,
                    event=event,
                  
                )

                serializer = GeneralMessageSerializer(message)
              
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            except Event.DoesNotExist:
               
                return Response({'error': 'Invalid event name'}, status=status.HTTP_400_BAD_REQUEST)
             
            except Exception as e:
             
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
        
            return Response({'error': 'Content is required'}, status=status.HTTP_400_BAD_REQUEST)



class GeneralMessageListView(APIView):
    def get(self, request, event_name=None, format=None):
        current_date = date.today()

        # Debugging print statement to check the event_name value
        print(f"Received event_name: {event_name}")

        if event_name:
            print(f"Fetching messages for event_name: {event_name}")
            messages = GeneralMessage.objects.select_related('event', 'author__userprofile').filter(
                event__event_name=event_name,
                timestamp__date=current_date
            )
        else:
            print("Fetching messages without event_name")
            messages = GeneralMessage.objects.select_related('event', 'author__userprofile').filter(
                timestamp__date=current_date
            )

        # Serialize the messages
        serializer = GeneralMessageSerializersChat(messages, many=True)
        data = serializer.data

        return JsonResponse(data, safe=False)



class GeneralMessageUpdateView(APIView):
    def put(self, request, pk):
        try:
            message = GeneralMessage.objects.get(pk=pk)
        except GeneralMessage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # Toggle the 'answered' field
        message.answered = not message.answered
        message.save()

        serializer = GeneralMessageSerializer(message)
        return Response(serializer.data)


 