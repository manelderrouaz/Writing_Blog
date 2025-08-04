from django.urls import path 
from .views import (
    StoryCreateView,
    StoryListView,
    StoryDetailView,
    StoryUpdateView,
    StoryDeleteView
)

urlpatterns = [
    path('stories/', StoryListView.as_view(), name='story-list'),
    path('stories/create/', StoryCreateView.as_view(), name='story-create'),
    path('stories/<int:pk>/', StoryDetailView.as_view(), name='story-detail'),
    path('stories/<int:pk>/update/', StoryUpdateView.as_view(), name='story-update'),
    path('stories/<int:pk>/delete/', StoryDeleteView.as_view(), name='story-delete'),
]
