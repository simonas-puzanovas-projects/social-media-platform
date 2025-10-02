from ..services import friendship_service

def find_friendship(user1_id, user2_id, status=None):
    """Find friendship between two users (handles bidirectional relationship)"""
    return friendship_service.find_friendship(user1_id, user2_id, status)

def get_friendship_status(current_user_id, other_user_id):
    """Get friendship status between current user and another user"""
    return friendship_service.get_friendship_status(current_user_id, other_user_id)

def get_friends_query(current_user_id):
    """Get query for accepted friends of current user"""
    return friendship_service.get_friends_query(current_user_id)