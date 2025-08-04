from rest_framework import serializers
from .models import Author,Story   

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
