from django.contrib import admin
from .models import Author,Story,Tag,Comment,Library,LibraryStory,Like,Follower,Notification
# Register your models here.
admin.site.register(Author)
admin.site.register(Story)
admin.site.register(Tag)
admin.site.register(Comment)
admin.site.register(Library)
admin.site.register(LibraryStory)
admin.site.register(Like)
admin.site.register(Follower)
admin.site.register(Notification)




