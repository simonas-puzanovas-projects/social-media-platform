from .. import socketio, db
from flask_socketio import join_room, leave_room, emit
from flask import session
from ..models import User, Message
from datetime import datetime

@socketio.on('connect')
def on_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        join_room(f'user_{user_id}')
        
        # Update user online status
        user = User.query.get(user_id)
        if user:
            user.is_online = True
            user.last_seen = datetime.utcnow()
            db.session.commit()

@socketio.on('disconnect')
def on_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        leave_room(f'user_{user_id}')

        # Update user offline status
        user = User.query.get(user_id)
        if user:
            user.is_online = False
            user.last_seen = datetime.utcnow()
            db.session.commit()

@socketio.on('mark_read')
def mark_messages_read(data):
    if 'user_id' not in session:
        return

    current_user_id = session['user_id']
    friend_id = data.get('friend_id')

    if not friend_id:
        return

    # Mark all messages from friend as read
    messages = Message.query.filter(
        Message.sender_id == friend_id,
        Message.receiver_id == current_user_id,
        Message.is_read == False
    ).all()

    message_ids = []
    for message in messages:
        message.is_read = True
        message_ids.append(message.id)

    db.session.commit()

    # Notify sender that messages were read
    if message_ids:
        print(f"Emitting messages_read to user_{friend_id}: {message_ids}")
        emit('messages_read', {'message_ids': message_ids, 'friend_id': current_user_id}, room=f'user_{friend_id}')
