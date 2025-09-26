from werkzeug.security import generate_password_hash
from ..models import User

class UserAlreadyExistsError(Exception): pass

class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, username, password):
        if User.query.filter_by(username=username).first():
            raise UserAlreadyExistsError
        
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        
        self.db.session.add(new_user)
        self.db.session.commit()


