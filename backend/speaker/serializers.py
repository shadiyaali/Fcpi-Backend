# users/serializers.py

from .models import Message 
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import SecondUser

class SecondUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SecondUser
        fields = ['id','username', 'password']

    def create(self, validated_data):
        # Hash the password before saving
        password = validated_data.pop('password')
        hashed_password = make_password(password)
        validated_data['password'] = hashed_password

        return super().create(validated_data)

 

from rest_framework import serializers
from .models import Message
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

User = get_user_model()  # Retrieve the custom user model

class MessageSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'content', 'author', 'timestamp']

