from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, Friendship

class UserServiceError(Exception): pass

class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, username, password):
        if User.query.filter_by(username=username).first():
            raise UserServiceError("User already exists.")
        
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

    def get_user_friends(self, user_id):
        friend_friendship_query = self.db.session.query(User, Friendship).join( Friendship, (User.id == Friendship.requester_id) | (User.id == Friendship.requested_id)
            ).filter( Friendship.status == 'accepted', ((Friendship.requester_id == user_id) | (Friendship.requested_id == user_id)),
            User.id != user_id).all()
        
        friends = []

        for user, friendship in friend_friendship_query:
            friends.append(user.to_public_data())
        
        return friends

        




        
        



    
