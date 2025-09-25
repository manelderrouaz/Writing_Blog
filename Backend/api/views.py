#from crypt import methods
import select
import stat
from django.shortcuts import render
from rest_framework import generics, permissions
from rest_framework.response import Response  
from rest_framework.views import APIView 
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.generics import (
    ListAPIView,
    CreateAPIView,
    DestroyAPIView
)
from .models import Author, Story, Tag, Like, Comment, Follower, Library, LibraryStory,Notification
from .serializer import LibraryStorySerializer, StorySerializer, TagSerializer, LikeSerializer, CommentSerializer, FollowerSerializer, LibrarySerializer, NotificationSerializer
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


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all()
    serializer_class = StorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

# Tag views 

class TagViewSet(viewsets.ModelViewSet):
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

class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['list_by_story', 'count_by_story']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def perform_create(self, serializer):
        # For direct POST /likes/ with body { story: id }
        serializer.save(user=self.request.user) 

    @action(detail=False, methods=['get'], url_path='story/(?P<story_id>[^/.]+)')
    def list_by_story(self, request, story_id=None):
        queryset = Like.objects.filter(story_id=story_id)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='story/(?P<story_id>[^/.]+)/create')
    def like_story(self, request, story_id=None):
        story = get_object_or_404(Story, id=story_id)
        like, created = Like.objects.get_or_create(user=request.user, story=story)
        if not created:
            return Response({'detail': 'Already liked'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(like)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='story/(?P<story_id>[^/.]+)/delete')
    def unlike_story(self, request, story_id=None):
        like = get_object_or_404(Like, story_id=story_id, user=request.user)
        like.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='story/(?P<story_id>[^/.]+)/count')
    def count_by_story(self, request, story_id=None):
        count = Like.objects.filter(story_id=story_id).count()
        return Response({'story_id': int(story_id), 'like_count': count})

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
    
    @action(detail=False, methods=['get'], url_path ="user/(?P<user_id>[^/.]+)/libraries", permission_classes=[IsAuthenticated,IsOwnerOrReadOnly])
    def user_libs(self,request, user_id=None):
        logged_user = request.user
        User = get_user_model()
        target_user = get_object_or_404(User,id=user_id)
        if logged_user == target_user:
            queryset = Library.objects.filter(user=target_user)
        else:
            queryset = Library.objects.filter(user=target_user, is_private=False)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)   


class LibraryStoryViewset(viewsets.ModelViewSet):
    queryset = LibraryStory.objects.all()
    serializer_class = LibraryStorySerializer
    permission_classes = [IsAuthenticated]
    @action(detail=False, methods=['post'], url_path='story/(?P<story_id>[^/.]+)/add-to-library')
    def add_story_to_library(self, request, story_id=None):
        library_id = request.data.get('library_id')
        if not library_id:
            return Response({'detail': 'library_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        target_library = get_object_or_404(Library, id=library_id, user=request.user)
        saved_story = get_object_or_404(Story, id=story_id)

        relation, created = LibraryStory.objects.get_or_create(library=target_library, story=saved_story)
        if not created:
            return Response({'detail': 'this post is already in library'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(relation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'], url_path='story/(?P<story_id>[^/.]+)/remove-from-library')
    def remove_story_from_library(self, request, story_id=None):
        library_id = request.data.get('library_id')
        if not library_id:
            return Response({'detail': 'library_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        target_library = get_object_or_404(Library, id=library_id, user=request.user)
        saved_story = get_object_or_404(Story, id=story_id)
        relation = get_object_or_404(LibraryStory, library=target_library, story=saved_story)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

    @action(detail=False,methods=['get'],url_path='library/(?P<lib_id>[^/.]+)/get-all-stories')
    def get_all_stories(self,request,lib_id=None):
        try:
            library = get_object_or_404(Library, id=lib_id)

            if library.is_privite and library.user != request.user :
                return Response({"detail":"you don't have the permission to access this library"},status=status.HTTP_403_FORBIDDEN)
            
            library_stories = LibraryStory.objects.filter(library=library).select_related('story','story__author')

            stories = [lib_story.story for lib_story in library_stories]

            serialiser = StorySerializer(stories, many=True)

            page = self.paginate_queryset(stories)

            if page is not None :
                serialiser = StorySerializer(page, many =True)
                return self.paginated_response(serialiser.data)
            
            return Response(serialiser.data)

        except ValueError:
            return Response({"detail":"Invalide libraru ID"},status=status.HTTP_200_successful) 


"""each time a new notification type is added a new notification row will be added to Notification, return all notifation filtred by authenticated user
if notification is not read """
class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all().select_related('recipient','sender','story','comment')
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset().filter(recipient=self.request.user)
        notif_type = self.request.query_params.get('type')
        is_read = self.request.query_params.get('is_read')
        if notif_type:
            queryset = queryset.filter(notif_type=notif_type)
        if is_read is not None:
            if is_read.lower() in ['true','1','yes']:
                queryset = queryset.filter(is_read=True)
            elif is_read.lower() in ['false','0','no']:
                queryset = queryset.filter(is_read=False)
        return queryset.order_by('-created_at')

    def perform_create(self, serializer):
        # Creation is handled by signals; disallow manual creation via API
        return Response({'detail': 'Creation is handled automatically'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        updated = self.get_queryset().update(is_read=True)
        return Response({'updated': updated})

