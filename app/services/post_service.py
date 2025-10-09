from PIL import Image
import os
import uuid
from ..models import Post, User, PostLike, PostComment

from .user_service import UserService
from ..services import user_service

class PostServiceError(Exception): pass

class PostService:

    def __init__(self, db):
        self.db = db

    def query_posts(self, profile_user_id=None):
        try:
            if profile_user_id:
                posts = self.db.session.query(Post)\
                                    .join(User, Post.owner == User.id)\
                                    .filter(User.id == profile_user_id)\
                                    .order_by(Post.created_at.desc())\
                                    .limit(50)\
                                    .all()
                posts_to_dict = [post.to_dict() for post in posts]
                return posts_to_dict

            else:
                posts = self.db.session.query(Post)\
                                    .order_by(Post.created_at.desc())\
                                    .limit(50)\
                                    .all()
                
                posts_to_dict = [post.to_dict() for post in posts]
                return posts_to_dict

        except Exception as e:
            print("message:", e)
            raise PostServiceError(e)
    
    def create_post(self, user_id, file):

            upload_folder = os.path.join('app', 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)

            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(upload_folder, unique_filename)

            file.save(file_path)

            new_post = Post(
                owner=user_id,
                image_path=f"uploads/{unique_filename}"
            )

            self.db.session.add(new_post)
            self.db.session.commit()

            return new_post

    def create_like(self, user_id, post_id):
        try:
            new_like = PostLike(
                user_id = user_id,
                post_id = post_id
            )
            self.db.session.add(new_like)
            self.db.session.commit()

        except Exception as e:
            self.db.rollback()
            raise PostServiceError(e)

    def delete_post(self, user_id, post_id):
        post = Post.query.filter_by(id=post_id, owner=user_id).first()
        if not post:
            raise PostServiceError("Post not found or not authorized")

        try:
            image_path = os.path.join('app', 'static', post.image_path)
            if os.path.exists(image_path):
                os.remove(image_path)

            self.db.session.delete(post)
            self.db.session.commit()
            return True

        except Exception as e:
            self.db.session.rollback()
            raise Exception(e)

    def query_post_likes(self, post_id):
        return Post.query.get(post_id).likes

    def remove_like(self, like_id):
        try:
            like = PostLike.query.filter_by(id=like_id).first()
            self.db.session.delete(like)
            self.db.session.commit()

        except Exception as e:
            self.db.rollback()
            raise PostServiceError(e)

    # Comment methods
    def create_comment(self, user_id, post_id, content, parent_id=None):
        """Create a new comment or reply to a comment"""
        try:
            if not content or not content.strip():
                raise PostServiceError("Comment content cannot be empty")

            # Verify post exists
            post = Post.query.get(post_id)
            if not post:
                raise PostServiceError("Post not found")

            # If parent_id provided, verify parent comment exists and belongs to same post
            if parent_id:
                parent_comment = PostComment.query.get(parent_id)
                if not parent_comment or parent_comment.post_id != post_id:
                    raise PostServiceError("Invalid parent comment")

            new_comment = PostComment(
                user_id=user_id,
                post_id=post_id,
                content=content.strip(),
                parent_id=parent_id
            )

            self.db.session.add(new_comment)
            self.db.session.commit()
            return new_comment

        except PostServiceError:
            self.db.session.rollback()
            raise
        except Exception as e:
            self.db.session.rollback()
            raise PostServiceError(str(e))

    def get_post_comments(self, post_id):
        """Get all top-level comments for a post with their replies"""
        try:
            # Get only top-level comments (parent_id is None)
            comments = PostComment.query.filter_by(
                post_id=post_id,
                parent_id=None
            ).order_by(PostComment.id.asc()).all()

            return comments

        except Exception as e:
            raise PostServiceError(str(e))

    def get_comment_count(self, post_id):
        """Get total count of comments (including replies) for a post"""
        try:
            count = PostComment.query.filter_by(post_id=post_id).count()
            return count
        except Exception as e:
            raise PostServiceError(str(e))

    def delete_comment(self, user_id, comment_id):
        """Delete a comment if user is the owner"""
        try:
            comment = PostComment.query.filter_by(id=comment_id, user_id=user_id).first()
            if not comment:
                raise PostServiceError("Comment not found or not authorized")

            # Cascade delete will handle replies due to model definition
            self.db.session.delete(comment)
            self.db.session.commit()
            return True

        except PostServiceError:
            self.db.session.rollback()
            raise
        except Exception as e:
            self.db.session.rollback()
            raise PostServiceError(str(e))





    def validate_image(self, file):
        if file.filename == '':
             raise PostServiceError('No file selected')

        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
             raise PostServiceError('Invalid file type. Only images allowed.')

        try:
            # Validate image by opening it
            img = Image.open(file.stream)
            img.verify()
            file.stream.seek(0)  # Reset stream after verification

            # Check image size (max 10MB)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > 10 * 1024 * 1024:  # 10MB limit
                raise PostServiceError('File too large. Maximum size is 10MB.')
            
            return file
        
        except Exception as e:
            raise PostServiceError(str(e))


