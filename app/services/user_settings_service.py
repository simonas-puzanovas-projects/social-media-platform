from werkzeug.security import generate_password_hash, check_password_hash
from PIL import Image
import os
import uuid
from ..models import User

class UserSettingsServiceError(Exception): pass

class UserSettingsService:
    def __init__(self, db):
        self.db = db

    def get_user_settings(self, user_id):
        """Get user settings data"""
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise UserSettingsServiceError("User not found")

        return {
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'bio': user.bio,
            'avatar_path': user.avatar_path
        }

    def update_profile(self, user_id, display_name=None, bio=None):
        """Update user profile information"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserSettingsServiceError("User not found")

            if display_name is not None:
                # Validate display name length
                if len(display_name) > 100:
                    raise UserSettingsServiceError("Display name too long (max 100 characters)")
                user.display_name = display_name.strip() if display_name.strip() else None

            if bio is not None:
                # Validate bio length
                if len(bio) > 500:
                    raise UserSettingsServiceError("Bio too long (max 500 characters)")
                user.bio = bio.strip() if bio.strip() else None

            self.db.session.commit()
            return self.get_user_settings(user_id)

        except UserSettingsServiceError:
            self.db.session.rollback()
            raise
        except Exception as e:
            self.db.session.rollback()
            raise UserSettingsServiceError(str(e))

    def change_password(self, user_id, old_password, new_password):
        """Change user password with verification"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserSettingsServiceError("User not found")

            # Verify old password
            if not check_password_hash(user.password_hash, old_password):
                raise UserSettingsServiceError("Current password is incorrect")

            # Validate new password
            if not new_password or len(new_password) < 6:
                raise UserSettingsServiceError("New password must be at least 6 characters")

            # Update password
            user.password_hash = generate_password_hash(new_password)
            self.db.session.commit()
            return True

        except UserSettingsServiceError:
            self.db.session.rollback()
            raise
        except Exception as e:
            self.db.session.rollback()
            raise UserSettingsServiceError(str(e))

    def upload_avatar(self, user_id, file):
        """Upload and set user avatar"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserSettingsServiceError("User not found")

            # Validate image
            validated_file = self._validate_image(file)

            # Create avatars directory
            upload_folder = os.path.join('app', 'static', 'uploads', 'avatars')
            os.makedirs(upload_folder, exist_ok=True)

            # Delete old avatar if exists
            if user.avatar_path:
                old_avatar_path = os.path.join('app', 'static', user.avatar_path)
                if os.path.exists(old_avatar_path):
                    try:
                        os.remove(old_avatar_path)
                    except Exception as e:
                        print(f"Failed to delete old avatar: {e}")

            # Save new avatar
            file_extension = validated_file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
            file_path = os.path.join(upload_folder, unique_filename)

            validated_file.save(file_path)

            # Update user avatar path
            user.avatar_path = f"uploads/avatars/{unique_filename}"
            self.db.session.commit()

            return user.avatar_path

        except UserSettingsServiceError:
            self.db.session.rollback()
            raise
        except Exception as e:
            self.db.session.rollback()
            raise UserSettingsServiceError(str(e))

    def delete_account(self, user_id, password):
        """Delete user account with password confirmation"""
        try:
            user = User.query.filter_by(id=user_id).first()
            if not user:
                raise UserSettingsServiceError("User not found")

            # Verify password before deletion
            if not check_password_hash(user.password_hash, password):
                raise UserSettingsServiceError("Password is incorrect")

            # Delete avatar if exists
            if user.avatar_path:
                avatar_path = os.path.join('app', 'static', user.avatar_path)
                if os.path.exists(avatar_path):
                    try:
                        os.remove(avatar_path)
                    except Exception as e:
                        print(f"Failed to delete avatar: {e}")

            # Delete user (cascade will handle relationships)
            self.db.session.delete(user)
            self.db.session.commit()
            return True

        except UserSettingsServiceError:
            self.db.session.rollback()
            raise
        except Exception as e:
            self.db.session.rollback()
            raise UserSettingsServiceError(str(e))

    def _validate_image(self, file):
        """Validate uploaded image file"""
        if file.filename == '':
            raise UserSettingsServiceError('No file selected')

        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not file.filename.lower().endswith(tuple(allowed_extensions)):
            raise UserSettingsServiceError('Invalid file type. Only images allowed.')

        try:
            # Validate image by opening it
            img = Image.open(file.stream)
            img.verify()
            file.stream.seek(0)  # Reset stream after verification

            # Check image size (max 5MB for avatars)
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > 5 * 1024 * 1024:  # 5MB limit
                raise UserSettingsServiceError('File too large. Maximum size is 5MB.')

            return file

        except UserSettingsServiceError:
            raise
        except Exception as e:
            raise UserSettingsServiceError(f'Invalid image file: {str(e)}')
