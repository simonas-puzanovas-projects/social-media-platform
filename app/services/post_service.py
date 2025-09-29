from PIL import Image
import os
import uuid
from ..models import Post

from .user_service import UserService

class PostServiceError(Exception): pass

class PostService:

    def __init__(self, db):
        self.db = db

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
