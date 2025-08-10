from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response  
from rest_framework.views import APIView 
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView,
    DestroyAPIView
)
from .models import Story,Tag 
from .serializer import StorySerializer,TagSerializer
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from .permissions import IsAuthorOrReadOnly 

# Add these imports at the top of your views.py file (if not already there)
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

# Add this view function at the end of your views.py file
@ensure_csrf_cookie
@require_http_methods(["GET"])
def get_csrf_token(request):
    """
    API endpoint to get CSRF token
    """
    token = get_token(request)
    return JsonResponse({'csrftoken': token})


# to create a story 
@method_decorator(csrf_exempt, name='dispatch')
class StoryCreateView(CreateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated] 
    def perform_create(self, serializer):
        serializer.save(author=self.request.user) # logged in user is set as author 

# to list all stories  
@method_decorator(csrf_exempt, name='dispatch')
class StoryListView(ListAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [permissions.AllowAny]
# retrieve a story by ID
@method_decorator(csrf_exempt, name='dispatch')
class StoryDetailView(RetrieveAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    lookup_field = 'pk' 

# retrieve and update a story 
@method_decorator(csrf_exempt, name='dispatch')
class StoryUpdateView(RetrieveUpdateAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'pk'

@method_decorator(csrf_exempt, name='dispatch')
class StoryDeleteView(DestroyAPIView):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
    lookup_field = 'pk'

# Tag views 

@method_decorator(csrf_exempt, name='dispatch')
class TagListCreateAPIView(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@method_decorator(csrf_exempt, name='dispatch')
class TagRetrieveAPIView(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@method_decorator(csrf_exempt, name='dispatch')
class TagUpdateAPIView(generics.UpdateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

@method_decorator(csrf_exempt, name='dispatch')
class TagDestroyAPIView(generics.DestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]