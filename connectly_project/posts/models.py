from django.db import models
from django.contrib.auth.models import User as AuthUser # I import Django's built-in User for Like because my views.py uses request.user

# Create your models here.
class User(models.Model):
    # Custom user model for Connectly. Stores public profile info separate from Django's auth user.
    username = models.CharField(max_length=100, unique=True) # User's unique  username
    email = models.EmailField(unique=True)  # User's unique email
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created
    role = models.CharField(max_length=10, choices=[('admin', 'Admin'), ('user', 'User')], default='user')

    def __str__(self):
        return self.username


class Post(models.Model):
    """
    This represents a post on Connectly. Supports text, image, and video types.
    Image posts require file_size in metadata, video posts require duration.
    """
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    title = models.CharField(max_length=200)  # Title of the post
    content = models.TextField()  # The text content of the post
    author = models.ForeignKey(
        User, 
        related_name='posts', 
        on_delete=models.CASCADE)  # The user who created the post
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the post was created
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')  # Type of post
    metadata = models.JSONField(default=dict, blank=True)  # To store specific type of data (e.g., file_size for images, duration for videos)
    privacy = models.CharField(max_length=10, choices=[('public', 'Public'), ('private', 'Private')], default='public') 


    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    """
    Represents a comment on a post. Linked to both a User (author) and a Post.
    Deletes automatically if the related post or author is removed.
    """
    text = models.TextField()  
    author = models.ForeignKey(
        User, related_name='comments',  # access via user.comments.all()
        on_delete=models.CASCADE)  
    post = models.ForeignKey(
        Post, 
        related_name='comments',       # access via post.comments.all()
        on_delete=models.CASCADE)  
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the comment was created

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"
    

class Like(models.Model):
    """
    This represents a like on a post. A user can only like a post once
    enforced by the unique_together constraint on user and post.
    Uses Django's built-in AuthUser since likes are tied to authenticated sessions.
    """
    user = models.ForeignKey(
        AuthUser,
        related_name='likes',      # access via user.likes.all()
        on_delete=models.CASCADE
    )
    post = models.ForeignKey(
        Post,
        related_name='likes',      # access via post.likes.all()
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')   # prevents duplicate likes

    def __str__(self):
        return f"{self.user.username} liked Post {self.post.id}"

