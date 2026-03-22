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
    message = 'You must be an admin to perform this action.'

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        from posts.models import User as CustomUser
        try:
            custom_user = CustomUser.objects.get(username=request.user.username)
            return custom_user.role == 'admin'
        except CustomUser.DoesNotExist:
            return False


class IsOwnerOrAdmin(BasePermission):
    message = 'You do not have permission to modify this resource.'

    def has_object_permission(self, request, view, obj):
        from posts.models import User as CustomUser
        try:
            custom_user = CustomUser.objects.get(username=request.user.username)
            if custom_user.role == 'admin':
                return True
        except CustomUser.DoesNotExist:
            pass
        return obj.author.username == request.user.username
