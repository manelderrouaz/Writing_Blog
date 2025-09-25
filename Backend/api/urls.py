from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from .views import (
    LibraryViewset,
    StoryViewSet,
    TagViewSet,
    # Tag
    get_csrf_token,
    # Like
    LikeViewSet,
    # Comment
    CommentViewSet,
    SessionToJWTView,
    # follower 
    FollowerViewSet,
    # library-story 
    LibraryStoryViewset,
    NotificationViewSet
)

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'follower', FollowerViewSet, basename='follower')
router.register(r'library', LibraryViewset, basename='library') 
router.register(r'library-story',LibraryStoryViewset, basename='library-story')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'stories', StoryViewSet, basename='story')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'likes', LikeViewSet, basename='like')

urlpatterns = [ 
    path('csrf-token/', get_csrf_token, name='csrf-token'),  

    # Router
    path('', include(router.urls)), 

    # Exchange session auth for JWT (after social login)
    path('auth/session-to-jwt/', SessionToJWTView.as_view(), name='session-to-jwt'),
]
