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
    messages = db.relationship("Message", backref='Message.messenger_id')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    messenger_id = db.Column(db.Integer, db.ForeignKey('messenger.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    image_path = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Add relationship to User
    owner_user = db.relationship('User', backref=db.backref('posts', lazy=True))

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
