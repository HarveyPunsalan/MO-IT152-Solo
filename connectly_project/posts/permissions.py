from rest_framework.permissions import BasePermission


class IsPostAuthor(BasePermission):
    """
    Custom permission to only allow the author of a post to modify it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the author of the post
        return obj.author == request.user


class IsCommentAuthor(BasePermission):
    """
    Custom permission to only allow the author of a comment to modify it.
    """
    def has_object_permission(self, request, view, obj):
        # Check if the user is the author of the comment
        return obj.author == request.user

