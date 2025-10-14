
from flask import Blueprint, render_template, request, session, jsonify
from ..helpers import create_notification, clean_notification_data
from ..models import User, Notification, Messenger
from ..decorators import login_required
from .. import db
from ..services import user_service, friendship_service, notification_service

bp_friends = Blueprint("bp_friends", __name__)

@bp_friends.route('/friends')
@login_required
def friends():
    current_user_id = session['user_id']
    
    friends = user_service.get_user_friends(current_user_id)

    received_requests = friendship_service.get_received_friend_requests(current_user_id).all()
    
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
        status = friendship_service.get_friendship_status(current_user_id, user.id)
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
    
    try:
        new_friendship = friendship_service.send_friend_request(current_user_id, requested_user_id)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
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
    
    try:
        if response == 'accept':
            friendship = friendship_service.accept_friend_request(friendship_id, current_user_id)

            new_messenger = Messenger(
                first_user_id=friendship.requested_id,
                second_user_id=friendship.requester_id,
            )
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

            try:
                friend_id = friendship_service.reject_friend_request(friendship_id, current_user_id)

                notification_service.remove_friendship_history(
                    session["user_id"],
                    friend_id,
                    friendship_id
                )

            except Exception as e:
                return jsonify({'success': False, 'message': str(e)})

            return jsonify({'success': True, 'message': 'Friend request rejected'})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@bp_friends.route('/cancel_friend_request', methods=['POST'])
@login_required
def cancel_friend_request():
    friendship_id = request.json.get('friendship_id')
    current_user_id = session['user_id']
    
    try:
        friend_id = friendship_service.cancel_friend_request(friendship_id, current_user_id)

        notification_service.remove_friendship_history(
            session["user_id"],
            friend_id,
            friendship_id
        )

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': True, 'message': 'Friend request cancelled'})

@bp_friends.route('/remove_friend', methods=['POST'])
@login_required
def remove_friend():
    friend_user_id = request.json.get('friend_user_id')
    current_user_id = session['user_id']
    
    if friend_user_id == current_user_id:
        return jsonify({'success': False, 'message': 'Cannot remove yourself'})
    
    try:
        friendship_service.remove_friend(current_user_id, friend_user_id)
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
    
    return jsonify({'success': True, 'message': 'Friend removed successfully'})

# ============================================================================
# API ROUTES (JSON DATA)
# ============================================================================

@bp_friends.route('/api/friends')
@login_required
def get_friends_data():
    current_user_id = session['user_id']
    
    # Get accepted friends
    friends = friendship_service.get_friends_query(current_user_id).all()
    
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
    received_requests = friendship_service.get_received_friend_requests(current_user_id).all()
    
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
    sent_requests = friendship_service.get_sent_friend_requests(current_user_id).all()
    
    requests_data = []
    for user, friendship in sent_requests:
        requests_data.append({
            'id': user.id,
            'username': user.username,
            'friendship_id': friendship.id,
            'created_at': friendship.created_at.isoformat()
        })
    
    return jsonify(requests_data)