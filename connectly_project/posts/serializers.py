from rest_framework import serializers
from .models import User, Post, Comment, Like

class UserSerializer(serializers.ModelSerializer):
    #Serializes user data. Excludes sensitive fields like password.
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    """
    Serializes post data including a list of related comments.
    Comments are returned as string representations (read-only).
    """
    comments = serializers.StringRelatedField(many=True, read_only=True)

    # These fields are computed, not stored in the database
    like_count = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'author', 'created_at', 'post_type', 'metadata', 'comments', 'like_count', 'comment_count', 'privacy']

    def get_like_count(self, obj):
        # 'likes' is the related_name set in the Like model's FK to Post
        return obj.likes.count()

    def get_comment_count(self, obj):
        # 'comments' is the related_name set in the Comment model's FK to Post
        return obj.comments.count()

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializes comment data with validation to ensure
    the referenced post and author actually exist in the database.
    """
    class Meta: 
        model = Comment
        fields = ['id', 'text', 'author', 'post', 'created_at']

    def validate_post(self, value):
        # Make sure the post being commented on exists
        if not Post.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Post not found.")
        return value
    
    def validate_author(self, value):
        # Make sure the author exists in the custom user table
        if not User.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Author not found.")
        return value
    
class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ['id', 'user', 'post', 'created_at']
        read_only_fields = ['created_at']
        validators = []    # I add this to disables Django's default unique constraint message

    def validate(self, data):
        # Check if this user already liked this post before saving
        if Like.objects.filter(user=data['user'], post=data['post']).exists():
            raise serializers.ValidationError(
                "You have already liked this post."
            )
        return data