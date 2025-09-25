from ast import Module
from dataclasses import fields
from nt import read
from pyexpat import model
from rest_framework import serializers
from .models import Author,Story,Tag,Like, Comment,Follower ,Library,LibraryStory, Notification

class AuthorSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = Author
        fields = ('username', 'email', 'password')    



class StorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = '__all__' 
        read_only_fields = ['author'] 

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
        read_only_fields = ['user', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = '__all__'
        read_only_fields = ['author', 'created_at']

class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follower
        fields = '__all__'
        read_only_fields = ['follower', 'followed', 'followed_at']

class LibrarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Library
        fields = '__all__'
        read_only_fields = ['user','created_at']

class LibraryStorySerializer(serializers.ModelSerializer):
    class Meta:
        model=LibraryStory
        fields= "__all__"
        read_only_fields = ['added_at']

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['recipient', 'sender', 'created_at']
