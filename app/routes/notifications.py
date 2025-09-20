from flask import jsonify, Blueprint, session
from ..models import Notification, Friendship
from ..helpers import clean_notification_data
from ..decorators import login_required
from .. import db

bp_notifications = Blueprint("bp_notifications", __name__)

@bp_notifications.route('/notifications')
@login_required
def get_notifications():
    current_user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=current_user_id).order_by(
        Notification.created_at.desc()
    ).limit(50).all()
    
    # Filter out invalid friend request notifications and clean them up
    valid_notifications = []
    notifications_to_delete = []
    
    for notification in notifications:
        if notification.type == 'friend_request':
            data = clean_notification_data(notification.data)
            if data:
                friendship_id = data.get('friendship_id')
                
                # Check if the friendship still exists and is pending
                friendship = Friendship.query.filter_by(
                    id=friendship_id,
                    requested_id=current_user_id,
                    status='pending'
                ).first()
                
                if friendship:
                    # Friendship is still valid and pending
                    valid_notifications.append(notification)
                else:
                    # Friendship doesn't exist or is no longer pending, mark for deletion
                    notifications_to_delete.append(notification)
            else:
                # Invalid notification data, mark for deletion
                notifications_to_delete.append(notification)
        else:
            # Not a friend request notification, include it
            valid_notifications.append(notification)
    
    # Clean up invalid notifications
    if notifications_to_delete:
        for notification in notifications_to_delete:
            db.session.delete(notification)
        db.session.commit()
    
    return jsonify([notification.to_dict() for notification in valid_notifications])

@bp_notifications.route('/cleanup_notifications', methods=['POST'])
@login_required
def cleanup_notifications():
    """Clean up all stale friend request notifications for the current user"""
    current_user_id = session['user_id']
    notifications = Notification.query.filter_by(
        user_id=current_user_id,
        type='friend_request'
    ).all()
    
    deleted_count = 0
    for notification in notifications:
        data = clean_notification_data(notification.data)
        if data:
            friendship_id = data.get('friendship_id')
            
            # Check if the friendship still exists and is pending
            friendship = Friendship.query.filter_by(
                id=friendship_id,
                requested_id=current_user_id,
                status='pending'
            ).first()
            
            if not friendship:
                # Friendship doesn't exist or is no longer pending, delete notification
                db.session.delete(notification)
                deleted_count += 1
        else:
            # Invalid notification data, delete it
            db.session.delete(notification)
            deleted_count += 1
    
    if deleted_count > 0:
        db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Cleaned up {deleted_count} stale notifications'
    })