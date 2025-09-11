from flask import json
from ..models import Notification
from .. import socketio, db

def clean_notification_data(notification_data_str):
    """Safely parse notification data JSON"""
    if not notification_data_str:
        return None
    try:
        return json.loads(notification_data_str)
    except (json.JSONDecodeError, TypeError):
        return None

def create_notification(user_id, notification_type, message, data=None):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        data=json.dumps(data) if data else None
    )
    db.session.add(notification)
    db.session.commit()
    
    # Emit real-time notification
    socketio.emit('new_notification', notification.to_dict(), room=f'user_{user_id}')
    return notification