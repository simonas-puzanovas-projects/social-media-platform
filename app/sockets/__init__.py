from .. import socketio, db
from flask_socketio import join_room, leave_room
from flask import session
from ..models import User
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
