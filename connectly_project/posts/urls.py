from django.urls import path
from .views import UserListCreate, PostListCreate, PostDetailView, CommentListCreate, CreatePostView, LikePostView, CommentPostView, GetPostCommentsView, FeedView, AdminPostListView


urlpatterns = [
    path('users/', UserListCreate.as_view(), name='user-list-create'),
    path('posts/', PostListCreate.as_view(), name='post-list-create'),
    path('posts/create/', CreatePostView.as_view(), name='post-create'),
    
    # post_id is captured from the URL and passed directly to the view
    path('posts/<int:post_id>/like/', LikePostView.as_view(), name='like-post'),
    path('posts/<int:post_id>/comment/', CommentPostView.as_view(), name='comment-post'),
    path('posts/<int:post_id>/comments/', GetPostCommentsView.as_view(), name='get-post-comments'),
    
    # Placed after specific routes so Django doesn't confuse pk with post_id
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('comments/', CommentListCreate.as_view(), name='comment-list-create'),

    # News feed endpoint - sorting and pagination handled inside FeedView
    path('feed/', FeedView.as_view(), name='news-feed'),

    # ── Admin only endpoint --
    path('admin/posts/', AdminPostListView.as_view(), name='admin-post-list'),
]

