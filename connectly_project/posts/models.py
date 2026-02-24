from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=100, unique=True) # User's unique  username
    email = models.EmailField(unique=True)  # User's unique email
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the user was created

    def __str__(self):
        return self.username


class Post(models.Model):
    POST_TYPES = [
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    
    title = models.CharField(max_length=200)  # Title of the post
    content = models.TextField()  # The text content of the post
    author = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)  # The user who created the post
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the post was created
    post_type = models.CharField(max_length=10, choices=POST_TYPES, default='text')  # Type of post
    metadata = models.JSONField(default=dict, blank=True)  # Metadata for the post (e.g., file_size for images, duration for videos)


    def __str__(self):
        return f"Post by {self.author.username} at {self.created_at}"


class Comment(models.Model):
    text = models.TextField()  # The text content of the comment
    author = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)  # The user who created the comment
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)  # The post being commented on
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp when the comment was created

    def __str__(self):
        return f"Comment by {self.author.username} on Post {self.post.id}"

