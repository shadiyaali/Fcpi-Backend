# users/serializers.py

from .models import Message ,GeneralMessage
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import SecondUser
from django.contrib.auth import get_user_model
from admins.serializers import SingleEventSerializer
from admins.models import Forum,Event
from accounts.models import UserProfile
from accounts.serializers import UserProfileSerializer
from admins.serializers import EventSerializer,ForumSerializer


class SecondUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondUser
        fields = ['id','username', 'password']

    def create(self, validated_data):
       
        password = validated_data.pop('password')
        hashed_password = make_password(password)
        validated_data['password'] = hashed_password

        return super().create(validated_data)

 

 


class MessageSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'author', 'author_name', 'timestamp']

    def get_author_name(self, obj):
        return obj.author.name() if obj.author else None
 

import pytz

class MessageSerializerChat(serializers.ModelSerializer):
    forum_name = serializers.CharField(source='forum.title', read_only=True)
    event_name = serializers.CharField(source='event.event_name', read_only=True)
    author_name = serializers.SerializerMethodField()
    timestamp = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'forum_name', 'event_name', 'author_name', 'timestamp']

    def get_author_name(self, obj):
        
        if obj.author:
            first_name = obj.author.first_name
            last_name = obj.author.last_name
            return f"{first_name} {last_name}".strip()  
        return 'Unknown'


    def get_timestamp(self, obj):
   
        return obj.timestamp.strftime('%Y-%m-%d %H:%M:%S')
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'forum', 'event', 'content', 'author', 'timestamp', 'answered']

class SecondUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondUser
        fields = ['id', 'username', 'password', 'status']



 

class MessageSerializersChat(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    event_name = serializers.CharField(source='event.event_name', read_only=True)
    forum_name = serializers.CharField(source='event.forum.title', read_only=True)
    author_profile = UserProfileSerializer(source='author.userprofile', read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'event_name', 'forum_name', 'content', 'timestamp', 'author_name', 'author_profile']

    def get_author_name(self, obj):
        # Combine first name and last name
        if obj.author:
            first_name = obj.author.first_name
            last_name = obj.author.last_name
            return f"{first_name} {last_name}".strip()   
        return 'Unknown'


class GeneralMessageSerializersChat(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()
    event_name = serializers.CharField(source='event.event_name', read_only=True)
  
    author_profile = UserProfileSerializer(source='author.userprofile', read_only=True)

    class Meta:
        model = GeneralMessage
        fields = ['id', 'event_name',  'content', 'timestamp', 'author_name', 'author_profile']

    def get_author_name(self, obj):
        # Combine first name and last name
        if obj.author:
            first_name = obj.author.first_name
            last_name = obj.author.last_name
            return f"{first_name} {last_name}".strip()   
        return 'Unknown'


class GeneralMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneralMessage
        fields = ['id', 'event', 'content', 'author', 'timestamp', 'answered']