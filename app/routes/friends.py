
from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from ..helpers import get_friendship_status, find_friendship, create_notification, clean_notification_data, get_friends_query
from ..models import User, Friendship, Notification, Messenger
from ..decorators import login_required
from .. import db
from ..services import user_service

bp_friends = Blueprint("bp_friends", __name__, template_folder="../templates")

@bp_friends.route('/friends')
@login_required
def friends():
    current_user_id = session['user_id']
    
    # Get accepted friends
    #friends = get_friends_query(current_user_id).all()
    friends = user_service.get_user_friends(current_user_id)
    
    # Get received friend requests
    received_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requester_id
    ).filter(
        Friendship.requested_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    return render_template('friends.html', friends=friends, received_requests=received_requests)

@bp_friends.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    users = User.query.filter(
        User.username.contains(query),
        User.id != session['user_id']
    ).limit(10).all()
    
    current_user_id = session['user_id']
    results = []
    
    for user in users:
        status = get_friendship_status(current_user_id, user.id)
        results.append({
            'id': user.id,
            'username': user.username,
            'status': status
        })
    
    return jsonify(results)

@bp_friends.route('/send_friend_request', methods=['POST'])
@login_required
def send_friend_request():
    requested_user_id = request.json.get('user_id')
    current_user_id = session['user_id']
    
    if requested_user_id == current_user_id:
        return jsonify({'success': False, 'message': 'Cannot send friend request to yourself'})
    
    existing_friendship = find_friendship(current_user_id, requested_user_id)
    if existing_friendship:
        return jsonify({'success': False, 'message': 'Friendship already exists or pending'})
    
    new_friendship = Friendship(
        requester_id=current_user_id,
        requested_id=requested_user_id,
        status='pending'
    )
    
    db.session.add(new_friendship)
    db.session.commit()
    
    # Create notification for the requested user
    requester = User.query.get(current_user_id)
    create_notification(
        requested_user_id,
        'friend_request',
        f'{requester.username} sent you a friend request',
        {'friendship_id': new_friendship.id, 'requester_username': requester.username}
    )
    
    return jsonify({'success': True, 'message': 'Friend request sent!'})

@bp_friends.route('/respond_friend_request', methods=['POST'])
@login_required
def respond_friend_request():
    friendship_id = request.json.get('friendship_id')
    response = request.json.get('response')
    current_user_id = session['user_id']
    
    friendship = Friendship.query.filter_by(
        id=friendship_id,
        requested_id=current_user_id,
        status='pending'
    ).first()
    
    if not friendship:
        return jsonify({'success': False, 'message': 'Friend request not found'})
    
    if response == 'accept':

        new_messenger = Messenger(
            first_user_id = friendship.requested_id,
            second_user_id = friendship.requester_id,
        )


        friendship.status = 'accepted'
        db.session.commit()
        db.session.add(new_messenger)
        db.session.commit()
        
        # Notify the requester that their request was accepted
        accepter = User.query.get(current_user_id)
        create_notification(
            friendship.requester_id,
            'friend_request_accepted',
            f'{accepter.username} accepted your friend request',
            {'friendship_id': friendship.id, 'accepter_username': accepter.username}
        )
        
        return jsonify({'success': True, 'message': 'Friend request accepted!'})
    elif response == 'reject':
        requester_id = friendship.requester_id
        
        # Delete any notifications related to this friend request
        related_notifications = Notification.query.filter_by(
            user_id=current_user_id,
            type='friend_request'
        ).all()
        
        for notification in related_notifications:
            data = clean_notification_data(notification.data)
            if data and data.get('friendship_id') == friendship_id:
                db.session.delete(notification)
        
        db.session.delete(friendship)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Friend request rejected'})
    
    return jsonify({'success': False, 'message': 'Invalid response'})

@bp_friends.route('/cancel_friend_request', methods=['POST'])
@login_required
def cancel_friend_request():
    friendship_id = request.json.get('friendship_id')
    current_user_id = session['user_id']
    
    friendship = Friendship.query.filter_by(
        id=friendship_id,
        requester_id=current_user_id,
        status='pending'
    ).first()
    
    if not friendship:
        return jsonify({'success': False, 'message': 'Friend request not found'})
    
    # Delete any notifications related to this friend request from the recipient's notifications
    related_notifications = Notification.query.filter_by(
        user_id=friendship.requested_id,
        type='friend_request'
    ).all()
    
    for notification in related_notifications:
        data = clean_notification_data(notification.data)
        if data and data.get('friendship_id') == friendship_id:
            db.session.delete(notification)
    
    # Delete the friendship request
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friend request cancelled'})

@bp_friends.route('/remove_friend', methods=['POST'])
@login_required
def remove_friend():
    friend_user_id = request.json.get('friend_user_id')
    current_user_id = session['user_id']
    
    if friend_user_id == current_user_id:
        return jsonify({'success': False, 'message': 'Cannot remove yourself'})
    
    # Find the friendship (could be either direction)
    friendship = find_friendship(current_user_id, friend_user_id, status='accepted')
    
    if not friendship:
        return jsonify({'success': False, 'message': 'Friendship not found'})
    
    # Delete the friendship
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friend removed successfully'})

# ============================================================================
# API ROUTES (JSON DATA)
# ============================================================================

@bp_friends.route('/api/friends')
@login_required
def get_friends_data():
    current_user_id = session['user_id']
    
    # Get accepted friends
    friends = get_friends_query(current_user_id).all()
    
    friends_data = []
    for user, friendship in friends:
        friends_data.append({
            'id': user.id,
            'username': user.username,
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None
        })
    
    return jsonify(friends_data)

@bp_friends.route('/api/friend_requests')
@login_required
def get_friend_requests_data():
    current_user_id = session['user_id']
    
    # Get received friend requests
    received_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requester_id
    ).filter(
        Friendship.requested_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    requests_data = []
    for user, friendship in received_requests:
        requests_data.append({
            'id': user.id,
            'username': user.username,
            'friendship_id': friendship.id,
            'created_at': friendship.created_at.isoformat()
        })
    
    return jsonify(requests_data)

@bp_friends.route('/api/sent_requests')
@login_required
def get_sent_requests_data():
    current_user_id = session['user_id']
    
    # Get sent friend requests that are still pending
    sent_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requested_id
    ).filter(
        Friendship.requester_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    requests_data = []
    for user, friendship in sent_requests:
        requests_data.append({
            'id': user.id,
            'username': user.username,
            'friendship_id': friendship.id,
            'created_at': friendship.created_at.isoformat()
        })
    
    return jsonify(requests_data)