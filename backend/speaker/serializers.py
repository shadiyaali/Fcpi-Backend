# users/serializers.py

from .models import Message 
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import SecondUser
from django.contrib.auth import get_user_model
from admins.serializers import SingleEventSerializer
from admins.models import Forum,Event


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

class MessageSerializerChat(serializers.ModelSerializer):
    forum_name = serializers.CharField(source='forum.title', read_only=True)
    event_name = serializers.CharField(source='event.event_name', read_only=True)
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'content', 'forum_name', 'event_name', 'author_name', 'timestamp']

    def get_author_name(self, obj):
        return obj.author.name() if obj.author else None



