from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Post, Comment, User as CustomUser
from .serializers import UserSerializer, PostSerializer, CommentSerializer, LikeSerializer
from .permissions import IsPostAuthor, IsCommentAuthor, IsAdminUser, IsOwnerOrAdmin
from singletons.logger_singleton import LoggerSingleton
from singletons.config_manager import ConfigManager
from factories.post_factory import PostFactory
from django.db.models import Q
from django.core.cache import cache


logger = LoggerSingleton().get_logger()


class UserListCreate(APIView):
    # Handles listing all users (GET) and creating a new user (POST).
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        # Use Django's create_user method for secure password hashing
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        
        # To generate a token for the new user on registration
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        
        logger.info(f"New user created: {username}")
        
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class PostListCreate(APIView):
    # Handles listing all posts (GET) and creating a new post (POST). Requires authentication.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # -- Check if requester is admin --
        try:    
            custom_user = CustomUser.objects.get(username=request.user.username)
            is_admin = custom_user.role == 'admin'
        except CustomUser.DoesNotExist:
            custom_user = None
            is_admin = False

        # Admins see all posts, regular users only see public posts + their own private posts
        if is_admin:
            posts = Post.objects.all()
        else:
            posts = Post.objects.filter(
                Q(privacy='public') | Q(author=custom_user)
            )
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Post created by user: {request.user.username}")

            # Invalidate feed cache when new post is created
            for p in range(1, 6):
                cache.delete(f'feed_{request.user.id}_page{p}_size20')
            logger.info(f"Feed cache invalidated after new post by {request.user.username}")

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Post creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    # Returns a single post by ID. Checks privacy, ownership, and role.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        # -- Check if requester is admin --
        try:
            custom_user = CustomUser.objects.get(username=request.user.username)
            is_admin = custom_user.role == 'admin'
        except CustomUser.DoesNotExist:
            is_admin = False

        # -- Privacy check --
        if (
            post.privacy == 'private' and
            post.author.username != request.user.username and
            not is_admin
        ):
            logger.warning(f"User {request.user.username} tried to view private post {pk}")
            return Response({'error': 'This post is private.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post)
        return Response(serializer.data)

    def delete(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        # -- Ownership check --
        permission = IsOwnerOrAdmin()
        if not permission.has_object_permission(request, self, post):
            logger.warning(f"User {request.user.username} tried to delete post {pk} — DENIED")
            return Response({'error': 'You do not have permission to delete this post.'}, status=status.HTTP_403_FORBIDDEN)

        post.delete()
        logger.info(f"User {request.user.username} deleted post {pk}")
        return Response({'message': 'Post deleted successfully.'}, status=status.HTTP_200_OK)
    
    def put(self, request, pk):
        try:
            post = Post.objects.get(pk=pk)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found.'}, status=status.HTTP_404_NOT_FOUND)

        # -- Ownership check --
        permission = IsOwnerOrAdmin()
        if not permission.has_object_permission(request, self, post):
            logger.warning(f"User {request.user.username} tried to edit post {pk} — DENIED")
            return Response({'error': 'You do not have permission to edit this post.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = PostSerializer(post, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.username} updated post {pk}")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CommentListCreate(APIView):
    # Handles listing all comments (GET) and creating a new comment (POST). Requires authentication.
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Comment created by user: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Comment creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePostView(APIView):
    # Creates a post using the PostFactory pattern. Validates post type and metadata.
    def post(self, request):
        data = request.data
        try:
            post = PostFactory.create_post(
                post_type=data['post_type'],
                title=data['title'],
                author_id=data['author'],
                content=data.get('content', ''),
                metadata=data.get('metadata', {})
            )
            return Response({'message': 'Post created successfully!', 'post_id': post.id}, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class LikePostView(APIView):
    """
    Handles liking a specific post (POST /posts/{id}/like/).
    Returns 404 if post doesn't exist, 400 if already liked, 201 on success.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        # Check if post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.warning(f"Like attempt on non-existent post id={post_id}")
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Build data and validate 
        data = {
            "user": request.user.id,
            "post": post.id
        }
        serializer = LikeSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.username} liked post {post_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Like failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class CommentPostView(APIView):
    """
    Handles commenting on a specific post (POST /posts/{id}/comment/).
    Returns 404 if post doesn't exist, 400 if text is empty, 201 on success.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        # Check if post exists
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.warning(f"Comment attempt on non-existent post id={post_id}")
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Author is automatically the logged in user
        data = {
            "text": request.data.get("text", ""),
            "author": request.data.get("author"),
            "post": post.id
        }
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"User {request.user.username} commented on post {post_id}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        logger.warning(f"Comment failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class GetPostCommentsView(APIView):
    """
    Retrieves all comments for a specific post (GET /posts/{id}/comments/).
    Returns 404 if post doesn't exist, 200 with empty list if no comments yet.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):  
        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            logger.warning(f"Comments requested for non-existent post id={post_id}")
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Fetch all comments for this post
        comments = Comment.objects.filter(post=post)
        serializer = CommentSerializer(comments, many=True)
        logger.info(f"Comments retrieved for post {post_id}")
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedPagination(PageNumberPagination):
    # Let clients control page size via ?page_size=N, but cap it at 100
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_page_size(self, request):
        # Check if client sent a custom page_size first
        if self.page_size_query_param in request.query_params:
            try:
                return min(
                    int(request.query_params[self.page_size_query_param]),
                    self.max_page_size
                )
            except ValueError:
                pass
        # Otherwise pull from ConfigManager instead of hardcoding it
        # so i only need to change it in one place if needed
        return ConfigManager().get_setting("DEFAULT_PAGE_SIZE")


class FeedView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Build cache key
        page = request.query_params.get('page', 1)
        page_size = request.query_params.get('page_size', 20)
        cache_key = f'feed_{request.user.id}_page{page}_size{page_size}'

        # Check cache first
        cached = cache.get(cache_key)   
        if cached:
            logger.info(f"Feed cache HIT for user {request.user.username}")
            return Response(cached)

        logger.info(f"Feed cache MISS for user {request.user.username}")

        # -- Check if requester is admin --
        try:
            custom_user = CustomUser.objects.get(username=request.user.username)
            is_admin = custom_user.role == 'admin'
        except CustomUser.DoesNotExist:
            custom_user = None
            is_admin = False

        # Admins see all posts, regular users only see public posts + their own private posts
        if is_admin:
            posts = Post.objects.all().order_by('-created_at')
        else:
            posts = Post.objects.filter(
                Q(privacy='public') | Q(author=custom_user)
            ).order_by('-created_at')

        # Slice the queryset into pages
        paginator = FeedPagination()
        paginated_posts = paginator.paginate_queryset(posts, request)

        # To serialize the current page
        serializer = PostSerializer(paginated_posts, many=True)

        logger.info(f"Feed accessed by user {request.user.username}")

        # To return count, next, previous, and results automatically
        response = paginator.get_paginated_response(serializer.data)

        # Store result in cache
        cache.set(cache_key, response.data, timeout=300)
        logger.info(f"Feed cached for user {request.user.username}")

        return response
    

class AdminPostListView(APIView):
    """
    Admin-only endpoint: GET /posts/admin/
    Returns ALL posts including private ones.
    Only users with role='admin' can access this.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        # Admin can see everything — no privacy filter
        posts = Post.objects.all().order_by('-created_at')
        serializer = PostSerializer(posts, many=True)
        logger.info(f"Admin {request.user.username} retrieved all posts")
        return Response(serializer.data, status=status.HTTP_200_OK)

