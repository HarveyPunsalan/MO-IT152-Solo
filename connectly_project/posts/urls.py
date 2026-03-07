from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate, CreatePostView, LikePostView, CommentPostView, GetPostCommentsView, FeedView


urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/create/', CreatePostView.as_view(), name='post-create'),
    # My 3 new path
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('posts/<int:post_id>/comment/', CommentPostView.as_view(), name='comment-post'),
    path('posts/<int:post_id>/comments/', GetPostCommentsView.as_view(), name='get-post-comments'),
    # I push this under because django reads url top to bottom
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),
    path('feed/', FeedView.as_view(), name='news-feed'),
]

