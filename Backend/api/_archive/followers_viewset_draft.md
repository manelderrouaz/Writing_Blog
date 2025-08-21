Follower endpoints draft (archived)

This file preserves the previous follower endpoints implementation so you can restore it later.

FollowerViewSet
```python
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from .models import Follower
from .serializer import FollowerSerializer


class FollowerViewSet(viewsets.ModelViewSet):
    queryset = Follower.objects.all()
    serializer_class = FollowerSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @action(detail=False, methods=['post'], url_path='user/(?P<user_id>[^/.]+)/follow', permission_classes=[permissions.IsAuthenticated])
    def follow(self, request, user_id=None):
        User = get_user_model()
        target_user = get_object_or_404(User, pk=user_id)
        if target_user == request.user:
            return Response({'detail': "You can't follow yourself."}, status=status.HTTP_400_BAD_REQUEST)
        follower_relation, created = Follower.objects.get_or_create(
            follower=request.user,
            followed=target_user,
        )
        if not created:
            return Response({'detail': 'Already following'}, status=status.HTTP_200_OK)
        serializer = self.get_serializer(follower_relation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post', 'delete'], url_path='user/(?P<user_id>[^/.]+)/unfollow', permission_classes=[permissions.IsAuthenticated])
    def unfollow(self, request, user_id=None):
        User = get_user_model()
        target_user = get_object_or_404(User, pk=user_id)
        try:
            relation = Follower.objects.get(follower=request.user, followed=target_user)
        except Follower.DoesNotExist:
            return Response({'detail': 'Not following'}, status=status.HTTP_404_NOT_FOUND)
        relation.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/followers', permission_classes=[permissions.AllowAny])
    def list_followers(self, request, user_id=None):
        queryset = Follower.objects.filter(followed_id=user_id).select_related('follower', 'followed')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/following', permission_classes=[permissions.AllowAny])
    def list_following(self, request, user_id=None):
        queryset = Follower.objects.filter(follower_id=user_id).select_related('follower', 'followed')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/followers/count', permission_classes=[permissions.AllowAny])
    def followers_count(self, request, user_id=None):
        count = Follower.objects.filter(followed_id=user_id).count()
        return Response({'user_id': int(user_id), 'followers_count': count})

    @action(detail=False, methods=['get'], url_path='user/(?P<user_id>[^/.]+)/following/count', permission_classes=[permissions.AllowAny])
    def following_count(self, request, user_id=None):
        count = Follower.objects.filter(follower_id=user_id).count()
        return Response({'user_id': int(user_id), 'following_count': count})
```

Router registration
```python
from rest_framework.routers import DefaultRouter
from .views import FollowerViewSet

router = DefaultRouter()
router.register(r'followers', FollowerViewSet, basename='follower')
```

Note: This is an archived draft only; it is not imported anywhere by default.


