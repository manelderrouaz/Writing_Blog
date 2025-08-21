from rest_framework import serializers
from .models import Author,Story,Tag,Like, Comment,Follower 

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
