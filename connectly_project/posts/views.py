from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from .models import Post, Comment, Like
from .serializers import UserSerializer, PostSerializer, CommentSerializer
from .permissions import IsPostAuthor, IsCommentAuthor
from singletons.logger_singleton import LoggerSingleton
from factories.post_factory import PostFactory


logger = LoggerSingleton().get_logger()


class UserListCreate(APIView):
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
        
        # Create authentication token for the user
        from rest_framework.authtoken.models import Token
        token, created = Token.objects.get_or_create(user=user)
        
        logger.info(f"New user created: {username}")
        
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'token': token.key
        }, status=status.HTTP_201_CREATED)


class PostListCreate(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)


    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"Post created by user: {request.user.username}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        logger.error(f"Post creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PostDetailView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated, IsPostAuthor]

    def get(self, request, pk):
        post = Post.objects.get(pk=pk)
        self.check_object_permissions(request, post)
        serializer = PostSerializer(post)
        return Response(serializer.data)


class CommentListCreate(APIView):
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
            "author": request.user.id,
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
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        # Check if post exists
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

