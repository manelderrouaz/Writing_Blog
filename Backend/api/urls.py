from django.urls import path 
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

)

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
]
