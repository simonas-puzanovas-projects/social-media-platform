from datetime import datetime
from flask import json
from .. import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    sent_requests = db.relationship('Friendship', 
                                  foreign_keys='Friendship.requester_id',
                                  backref='requester', 
                                  lazy='dynamic')
    received_requests = db.relationship('Friendship', 
                                      foreign_keys='Friendship.requested_id',
                                      backref='requested', 
                                      lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')
    post_likes = db.relationship('PostLike', backref = db.backref('user', lazy=True))


    def to_public_data(self):
        return {
            'id': self.id,
            'username': self.username,
            'is_online': self.is_online,
            'last_seen': self.last_seen.isoformat()
        }


class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Friendship {self.requester_id} -> {self.requested_id} ({self.status})>'

class Messenger(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    second_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messages = db.relationship("Message", backref='messenger')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messenger_id = db.Column(db.Integer, db.ForeignKey('messenger.id'))
    content = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PostLike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)

class PostComment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('post_comment.id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('comments', lazy=True))
    parent_comment = db.relationship("PostComment", backref=db.backref('replies', cascade='all, delete-orphan'), remote_side=[id])

    @property
    def reply_count(self):
        """Get count of direct replies to this comment"""
        return len(self.replies) if self.replies else 0

    def to_dict(self):
        """Convert comment to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username,
            'post_id': self.post_id,
            'parent_id': self.parent_id,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
            'reply_count': self.reply_count,
            'replies': [reply.to_dict() for reply in self.replies] if self.replies else []
        }

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner_user = db.relationship('User', backref=db.backref('posts', lazy=True))
    likes = db.relationship("PostLike", backref='post', cascade='all, delete-orphan')
    comments = db.relationship("PostComment", backref='post', cascade='all, delete-orphan')

    def to_dict(self):
        likes = [
            {
                "user_id": like.user_id,
                "username": like.user.username
            }
            for like in self.likes
        ]

        # Count all comments including nested replies
        def count_all_comments(comments):
            total = 0
            for comment in comments:
                total += 1
                if comment.replies:
                    total += count_all_comments(comment.replies)
            return total

        comment_count = count_all_comments([c for c in self.comments if c.parent_id is None])

        return {
            'id': self.id,
            'owner_id': self.owner,
            'owner_name': self.owner_user.username,
            'image_path': self.image_path,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            "likes": likes,
            "comment_count": comment_count
        }

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'data': json.loads(self.data) if self.data else None,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }
