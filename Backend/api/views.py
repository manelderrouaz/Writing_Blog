from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response  
from rest_framework.views import APIView 
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView
)
from .models import Story 
from .serializer import StorySerializer
from rest_framework.permissions import IsAuthenticated
from .permissions import IsAuthorOrReadOnly


# to create a story 
class StoryCreateView(CreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated] 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) # logged in user is set as author

# to list all stories  
class StoryListView(ListAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer

# retrieve a story by ID
class StoryDetailView(RetrieveAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    lookup_field = 'pk' 
# retrieve and update a story 
class StoryUpdateView(RetrieveUpdateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'pk'

class StoryDeleteView(DestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'pk'


