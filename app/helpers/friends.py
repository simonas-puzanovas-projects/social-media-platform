from ..models import Friendship, User
from .. import db

def find_friendship(user1_id, user2_id, status=None):
    """Find friendship between two users (handles bidirectional relationship)"""
    query = Friendship.query.filter(
        ((Friendship.requester_id == user1_id) & (Friendship.requested_id == user2_id)) |
        ((Friendship.requester_id == user2_id) & (Friendship.requested_id == user1_id))
    )
    if status:
        query = query.filter(Friendship.status == status)
    return query.first()

def get_friendship_status(current_user_id, other_user_id):
    """Get friendship status between current user and another user"""
    friendship = find_friendship(current_user_id, other_user_id)
    
    if not friendship:
        return 'none'
    elif friendship.status == 'accepted':
        return 'friends'
    elif friendship.requester_id == current_user_id:
        return 'request_sent'
    else:
        return 'request_received'

def get_friends_query(current_user_id):
    """Get query for accepted friends of current user"""
    return db.session.query(User, Friendship).join( Friendship, (User.id == Friendship.requester_id) | (User.id == Friendship.requested_id)
        ).filter( Friendship.status == 'accepted', ((Friendship.requester_id == current_user_id) | (Friendship.requested_id == current_user_id)),
        User.id != current_user_id)