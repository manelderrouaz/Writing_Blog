from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from .views import (
    StoryCreateView,
    StoryListView,
    StoryDetailView,
    StoryUpdateView,
    StoryDeleteView,
    # Tag
    TagListCreateAPIView,
    TagRetrieveAPIView,
    TagUpdateAPIView,
    TagDestroyAPIView,
    get_csrf_token,
    # Like
    LikeListView,
    LikeCreateView,
    LikeDeleteView,
    LikeCountView,
    # Comment
    CommentViewSet,
    SessionToJWTView,
)

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [ 

    path('stories/', StoryListView.as_view(), name='story-list'),
    path('stories/create/', StoryCreateView.as_view(), name='story-create'),
    path('stories/<int:pk>/', StoryDetailView.as_view(), name='story-detail'),
    path('stories/<int:pk>/update/', StoryUpdateView.as_view(), name='story-update'),
    path('stories/<int:pk>/delete/', StoryDeleteView.as_view(), name='story-delete'),
    # Tag
    path('tags/', TagListCreateAPIView.as_view(), name='tag-list-create'),
    path('tags/<int:pk>/', TagRetrieveAPIView.as_view(), name='tag-retrieve'),
    path('tags/<int:pk>/update/', TagUpdateAPIView.as_view(), name='tag-update'),
    path('tags/<int:pk>/delete/', TagDestroyAPIView.as_view(), name='tag-delete'),
    path('csrf-token/', get_csrf_token, name='csrf-token'),  

    # Like endpoints
    path('stories/<int:story_id>/likes/', LikeListView.as_view(), name='like-list'),
    path('stories/<int:story_id>/likes/create/', LikeCreateView.as_view(), name='like-create'),
    path('stories/<int:story_id>/likes/delete/', LikeDeleteView.as_view(), name='like-delete'),
    path('stories/<int:story_id>/likes/count/', LikeCountView.as_view(), name='like-count'),

    # Comment router
    path('', include(router.urls)),

    # Exchange session auth for JWT (after social login)
    path('auth/session-to-jwt/', SessionToJWTView.as_view(), name='session-to-jwt'),
]
