import select
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
from .models import Author, Story,Tag, Like, Comment,Follower,Library
from .serializer import StorySerializer,TagSerializer, LikeSerializer, CommentSerializer, FollowerSerializer,LibrarySerializer
from rest_framework.permissions import IsAuthenticated,IsAuthenticatedOrReadOnly
from .permissions import IsAuthorOrReadOnly, IsOwnerOrReadOnly 

# Add these imports at the top of your views.py file (if not already there)
from django.middleware.csrf import get_token
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods

from rest_framework import status, viewsets
from rest_framework.generics import ListAPIView, CreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

# from Backend.api import serializer Look it up 

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

# Like Views
class LikeListView(ListAPIView):
    serializer_class = LikeSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        story_id = self.kwargs.get('story_id')
        return Like.objects.filter(story_id=story_id)

class LikeCreateView(CreateAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        story_id = self.kwargs.get('story_id')
        story = get_object_or_404(Story, id=story_id)
        serializer.save(user=self.request.user, story=story)

class LikeDeleteView(DestroyAPIView):
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        story_id = self.kwargs.get('story_id')
        user = self.request.user
        return get_object_or_404(Like, story_id=story_id, user=user)

class LikeCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, story_id):
        count = Like.objects.filter(story_id=story_id).count()
        return Response({'story_id': story_id, 'like_count': count})

# Comment ViewSet
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user) 

    @action(detail=False, methods=['get'], url_path='story/(?P<story_id>[^/.]+)', permission_classes=[permissions.AllowAny])
    def list_by_story(self, request, story_id=None):
        queryset = Comment.objects.filter(story_id=story_id)
        page = self.paginate_queryset(queryset)
        if page is not None: 
            serializer = self.get_serializer(page, many=True) 
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='story/(?P<story_id>[^/.]+)/count', permission_classes=[permissions.AllowAny])
    def count_by_story(self, request, story_id=None):
        count = Comment.objects.filter(story_id=story_id).count()
        return Response({'story_id': int(story_id), 'comment_count': count})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reply(self, request, pk=None):
        parent_comment = self.get_object()
        content = request.data.get('content')
        if not content:
            return Response({'detail': 'content is required'}, status=status.HTTP_400_BAD_REQUEST)
        reply_comment = Comment.objects.create(
            story=parent_comment.story,
            author=request.user,
            content=content,
            parent=parent_comment,
        ) 
        serializer = self.get_serializer(reply_comment) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# Exchange authenticated session (e.g., after Google login) for JWT tokens
@method_decorator(csrf_exempt, name='dispatch')
class SessionToJWTView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = RefreshToken.for_user(request.user)
        return Response({
            'refresh': str(refresh_token),
            'access': str(refresh_token.access_token),
        })

"""
add a follow , Unfollow , get all followers , get all followings ,number of followers ,number of followings 
"""

class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer 
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=False,methods=['post'],url_path="user/(?P<user_id>[^/.]+)/follow",permission_classes=[IsAuthenticated])
    def follow(self,request,user_id=None):
            User = get_user_model()
            target_user = get_object_or_404(User,id=user_id) 
            if request.user == target_user:
                return Response({"detail":" you can not follow your self"},status=status.HTTP_400_BAD_REQUEST)
            follower_relation,created = Follower.objects.get_or_create(follower=request.user,followed=target_user)
            if not created:
                return Response({"detail":"you are already following this user"},status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(follower_relation)
            return Response(serializer.data,status=status.HTTP_201_CREATED) 
    
    @action(detail=False,methods=["post","delete"],url_path="user/(?P<user_id>[^/.]+)/unfollow",permission_classes=[IsAuthenticated])
    def unfollow(self,request,user_id=None):
        User = get_user_model()
        target_user = get_object_or_404(User,id=user_id)
        if request.user == target_user :
            return Response({"detail":"You can't unfollow yourself"},status=status.HTTP_400_BAD_REQUEST)
        
        try:
            relation = Follower.objects.get(follower=request.user,followed = target_user)
        except:
            return Response({"detail":"You are not following"}, status=status.HTTP_404_NOT_FOUND)
        
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False,methods=["get"],url_path="user/(?P<user_id>[^/.]+)/followers",permission_classes=[IsAuthenticated])
    def list_followers(self,request,user_id=None):
        queryset = Follower.objects.filter(followed_id = user_id).select_related('follower','followed') 
        page = self.paginate_queryset(queryset)
        if page is not None :
            serializer = self.get_serializer(page,many = True)
            return Response(serializer.data)
        serializer = self.get_serializer(queryset,many = True)
        return Response(serializer.data) 

    @action(detail=False,methods=["get"],url_path="user/(?P<user_id>[^/.]+)/followings",permission_classes=[IsAuthenticated])
    def list_followings(self,request,user_id=None):
        queryset = Follower.objects.filter(follower_id = user_id).select_related('follower','followed') 
        page = self.paginate_queryset(queryset)
        if page is not None :
            serializer = self.get_serializer(page,many = True)
            return Response(serializer.data)
        serializer = self.get_serializer(queryset,many = True)
        return Response(serializer.data)

    @action(detail=False,methods=["get"],url_path="user/(?P<user_id>[^/.]+)/followers/count",permission_classes=[IsAuthenticated])
    def count_followers(self,request,user_id=None):
        count = Follower.objects.filter(followed_id=user_id).count()
        return Response({"User Id": int(user_id), "Number of followers": count})
    
    @action(detail=False,methods=["get"],url_path="user/(?P<user_id>[^/.]+)/followings/count",permission_classes=[IsAuthenticated])
    def count_followings(self,request,user_id=None):
        count = Follower.objects.filter(follower_id=user_id).count()
        return Response({"User Id": int(user_id), "Number of followings": count})  

""" create library ,update , get a user libraries if they are public ,make a lib public,delete lib """

class LibraryViewset(viewsets.ModelViewSet):
    queryset = Library.objects.all()    
    serializer_class = LibrarySerializer
    permission_classes=[IsAuthenticatedOrReadOnly,IsOwnerOrReadOnly]

    def perform_create(self,serializer):
        serializer.save(user=self.request.user)  


