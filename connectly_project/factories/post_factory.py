from posts.models import Post, User


class PostFactory:
    @staticmethod
    def create_post(post_type, title, author_id, content='', metadata=None):
        if post_type not in dict(Post.POST_TYPES):
            raise ValueError("Invalid post type")


        # Validate type-specific requirements
        if post_type == 'image' and 'file_size' not in metadata:
            raise ValueError("Image posts require 'file_size' in metadata")
        if post_type == 'video' and 'duration' not in metadata:
            raise ValueError("Video posts require 'duration' in metadata")

        # Get the author
        author = User.objects.get(id=author_id)


        return Post.objects.create(
            title=title,
            content=content,
            post_type=post_type,
            metadata=metadata,
            author=author
        )

