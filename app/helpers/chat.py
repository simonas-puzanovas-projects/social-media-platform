from ..models import Friendship, User, Messenger
from .. import db

def get_user_messenger(user1_id, user2_id):
    """Get messenger between two users if they are friends"""
    return db.session.query(Messenger).filter(
        ((Messenger.first_user_id == user1_id) & (Messenger.second_user_id == user2_id)) |
        ((Messenger.first_user_id == user2_id) & (Messenger.second_user_id == user1_id))
    ).first()

