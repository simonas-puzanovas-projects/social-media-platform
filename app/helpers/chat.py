from ..models import Friendship, User, Messenger
from .. import db

def get_user_messenger(user1_id, user2_id):
    return db.session.query(Messenger).filter(
        Messenger,
        (user1_id == Messenger.first_user_id) and (user2_id == Messenger.second_user_id) or
        (user2_id == Messenger.first_user_id) and (user1_id == Messenger.second_user_id),
        Friendship.status == 'accepted').first()
        

