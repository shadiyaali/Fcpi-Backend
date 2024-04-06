# users/serializers.py

 
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

