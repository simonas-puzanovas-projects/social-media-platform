from ..models import User, Friendship

class FriendshipServiceError(Exception):
    pass

class FriendshipService:
    def __init__(self, db):
        self.db = db

    def find_friendship(self, user1_id, user2_id, status=None):
        """Find friendship between two users (handles bidirectional relationship)"""
        query = Friendship.query.filter(
            ((Friendship.requester_id == user1_id) & (Friendship.requested_id == user2_id)) |
            ((Friendship.requester_id == user2_id) & (Friendship.requested_id == user1_id))
        )
        if status:
            query = query.filter(Friendship.status == status)
        return query.first()

    def get_friendship_status(self, current_user_id, other_user_id):
        """Get friendship status between current user and another user"""
        friendship = self.find_friendship(current_user_id, other_user_id)

        if not friendship:
            return 'none'
        elif friendship.status == 'accepted':
            return 'friends'
        elif friendship.requester_id == current_user_id:
            return 'request_sent'
        else:
            return 'request_received'

    def get_friends_query(self, current_user_id):
        """Get query for accepted friends of current user"""
        return self.db.session.query(User, Friendship).join(
            Friendship, (User.id == Friendship.requester_id) | (User.id == Friendship.requested_id)
        ).filter(
            Friendship.status == 'accepted',
            ((Friendship.requester_id == current_user_id) | (Friendship.requested_id == current_user_id)),
            User.id != current_user_id
        )

    def get_user_friends(self, user_id):
        """Get list of user's friends with their public data"""
        friend_friendship_query = self.get_friends_query(user_id).all()

        friends = []
        for user, friendship in friend_friendship_query:
            friends.append(user.to_public_data())

        return friends

    def get_received_friend_requests(self, user_id):
        """Get pending friend requests received by the user"""
        return self.db.session.query(User, Friendship).join(
            Friendship, User.id == Friendship.requester_id
        ).filter(
            Friendship.requested_id == user_id,
            Friendship.status == 'pending'
        )

    def get_sent_friend_requests(self, user_id):
        """Get pending friend requests sent by the user"""
        return self.db.session.query(User, Friendship).join(
            Friendship, User.id == Friendship.requested_id
        ).filter(
            Friendship.requester_id == user_id,
            Friendship.status == 'pending'
        )

    def send_friend_request(self, requester_id, requested_id):
        """Send a friend request from requester to requested user"""
        if requester_id == requested_id:
            raise FriendshipServiceError('Cannot send friend request to yourself')

        existing_friendship = self.find_friendship(requester_id, requested_id)
        if existing_friendship:
            raise FriendshipServiceError('Friendship already exists or pending')

        new_friendship = Friendship(
            requester_id=requester_id,
            requested_id=requested_id,
            status='pending'
        )

        self.db.session.add(new_friendship)
        self.db.session.commit()
        return new_friendship

    def accept_friend_request(self, friendship_id, current_user_id):
        """Accept a friend request"""
        friendship = Friendship.query.filter_by(
            id=friendship_id,
            requested_id=current_user_id,
            status='pending'
        ).first()

        if not friendship:
            raise FriendshipServiceError('Friend request not found')

        friendship.status = 'accepted'
        self.db.session.commit()
        return friendship

    def reject_friend_request(self, friendship_id, current_user_id):
        """Reject a friend request"""
        friendship = Friendship.query.filter_by(
            id=friendship_id,
            requested_id=current_user_id,
            status='pending'
        ).first()

        if not friendship:
            raise FriendshipServiceError('Friend request not found')

        self.db.session.delete(friendship)
        self.db.session.commit()
        return friendship.requester_id

    def cancel_friend_request(self, friendship_id, current_user_id):
        """Cancel a sent friend request"""
        friendship = Friendship.query.filter_by(
            id=friendship_id,
            requester_id=current_user_id,
            status='pending'
        ).first()

        if not friendship:
            raise FriendshipServiceError('Friend request not found')

        requested_id = friendship.requested_id
        self.db.session.delete(friendship)
        self.db.session.commit()
        return requested_id

    def remove_friend(self, current_user_id, friend_user_id):
        """Remove a friend relationship"""
        if friend_user_id == current_user_id:
            raise FriendshipServiceError('Cannot remove yourself')

        friendship = self.find_friendship(current_user_id, friend_user_id, status='accepted')

        if not friendship:
            raise FriendshipServiceError('Friendship not found')

        self.db.session.delete(friendship)
        self.db.session.commit()
        return True