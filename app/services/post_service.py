from PIL import Image
import os
import uuid
from ..models import Post, User, PostLike

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
    
    def is_user_liked(self, user_id, post_id):
        likes = self.query_post_likes(post_id)
        for like in likes:
            if user_id == like.user_id:
                return True
        return False

    def remove_like(self, like_id):
        try:
            like = PostLike.query.filter_by(id=like_id).first()
            self.db.session.delete(like)
            self.db.session.commit()

        except Exception as e:
            self.db.rollback()
            raise PostServiceError(e)





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


