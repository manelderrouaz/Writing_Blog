from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.text import slugify
from django.conf import settings

# -------------------------------
# Custom User Model 
# -------------------------------
class Author(AbstractUser): 
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)

    gmail = models.EmailField(blank=True, null=True, help_text="Optional Gmail address")
    facebook_url = models.URLField(blank=True, null=True, help_text="Facebook profile link")

    created_at = models.DateTimeField(auto_now_add=True)

    groups = models.ManyToManyField(
        Group,
        related_name='author_set',
        blank=True,
        help_text='The groups this user belongs to.',
        related_query_name='author',
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='author_set',
        blank=True,
        help_text='Specific permissions for this user.',
        related_query_name='author',
    )

    def __str__(self):
        return self.username



# Story (Post)
# -------------------------------
class Story(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='stories')
    cover_image = models.ImageField(upload_to='covers/', blank=True, null=True)   
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    read_time = models.IntegerField(null=True, blank=True) 
    tags = models.ManyToManyField('Tag', related_name='stories', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    

# Tag
# -------------------------------
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

# Comment
# -------------------------------
class Comment(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')

    def __str__(self):
        return f'Comment by {self.author} on {self.story}'
    
# Like
# -------------------------------
class Like(models.Model):
    story = models.ForeignKey(Story, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)               

    class Meta:
        unique_together = ('story', 'user')  # prevents multiple likes

# Follower (Self-referencing M2M)
# -------------------------------
class Follower(models.Model): 
    follower =  models.ForeignKey(settings.AUTH_USER_MODEL, related_name='following', on_delete=models.CASCADE) 
    followed = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='followers', on_delete=models.CASCADE) 
    followed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('follower', 'followed')  # prevents duplicate follows


# Library (Custom Lists)
# -------------------------------
class Library(models.Model): 
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='libraries') 
    name = models.CharField(max_length=100) 
    description = models.TextField(blank=True)
    is_private = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} ({self.user.username})'

# -------------------------------
# LibraryStory (Many-to-Many through)
# -------------------------------
class LibraryStory(models.Model): # link the story to a library 
    library = models.ForeignKey(Library, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('library', 'story')


# Notification
# -------------------------------
class Notification(models.Model):
    NOTIF_TYPE_CHOICES = [
        ('like', 'Like'),
        ('comment', 'Comment'),
        ('follow', 'Follow'),
        ('story', 'Story Published'),
    ] 

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications') 
    notif_type = models.CharField(max_length=20, choices=NOTIF_TYPE_CHOICES)
    story = models.ForeignKey(Story, null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.notif_type} from {self.sender} to {self.recipient}' 
    


