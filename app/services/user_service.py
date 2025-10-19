from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, Friendship
import re

class UserServiceError(Exception): pass

class UserService:
    def __init__(self, db):
        self.db = db

    def _validate_username(self, username):
        """Validate username format and length"""
        if not username or len(username) < 3:
            raise UserServiceError("Username must be at least 3 characters long.")

        if len(username) > 20:
            raise UserServiceError("Username must not exceed 20 characters.")

        # Allow only alphanumeric characters and underscores
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise UserServiceError("Username can only contain letters, numbers, and underscores.")

    def _validate_password(self, password):
        """Validate password strength"""
        if not password or len(password) < 6:
            raise UserServiceError("Password must be at least 6 characters long.")

        if len(password) > 128:
            raise UserServiceError("Password must not exceed 128 characters.")

    def create_user(self, username, password):
        # Validate inputs
        self._validate_username(username)
        self._validate_password(password)

        if User.query.filter_by(username=username).first():
            raise UserServiceError("Username is already taken.")

        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)

        self.db.session.add(new_user)
        self.db.session.commit()

    def authenticate_user(self, username, password):
        user = User.query.filter_by(username=username).first()

        if not user:
            raise UserServiceError("User does not exists.")
        
        if not check_password_hash(user.password_hash, password):
            raise UserServiceError("Wrong password.")

        return user

    def get_user(self, user_id):
        user = User.query.filter_by(id=user_id).first()
        if not user:
            raise UserServiceError("User does not exist.")
        return user
    
    def get_user_by_name(self, username):
        user = User.query.filter_by(username=username).first()
        if not user:
            raise UserServiceError("User does not exist.")
        return user


    def get_user_friends(self, user_id):
        from ..services import friendship_service
        return friendship_service.get_user_friends(user_id)

        




        
        



    
