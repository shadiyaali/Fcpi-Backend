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

from rest_framework.authentication import TokenAuthentication


class SecondUserLoginView(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        
        try:
            user = SecondUser.objects.get(username=username)
            if check_password(password, user.password) and user.status == 'Active':
                return Response({'message': 'Login successful'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Invalid username, password, or user status'}, status=status.HTTP_400_BAD_REQUEST)
        except SecondUser.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)

 
from .models import SecondUser
from .serializers import SecondUserSerializer

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
        
        

class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [ ]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
 
 

 

class SendMessageAPIView(APIView):
    
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        content = request.data.get('content')
        author_id = request.data.get('author')
        print("Request Data:", request.data)

        if content and author_id:
            print("Content:", content)
            print("Author ID:", author_id)
            try:
                author = User.objects.get(id=author_id)
                message = Message.objects.create(content=content, author=author)
                serializer = MessageSerializer(message)
                print("Serialized Data:", serializer.data)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except User.DoesNotExist:
                return Response({'error': 'Invalid author ID'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Content and author ID are required'}, status=status.HTTP_400_BAD_REQUEST)

