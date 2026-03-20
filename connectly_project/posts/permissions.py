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

class IsAdminUser(BasePermission):
    """
    Only allows access to users with role='admin'.
    """
    message = 'You must be an admin to perform this action.'

    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            hasattr(request.user, 'role') and
            request.user.role == 'admin'
        )


class IsOwnerOrAdmin(BasePermission):
    """
    Only allows access if the user owns the object OR is an admin.
    """
    message = 'You do not have permission to modify this resource.'

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True
        return obj.author == request.user
