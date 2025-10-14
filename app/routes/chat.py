from flask import Blueprint, render_template, session, request, jsonify
from ..models import Messenger, Message, User
from ..decorators import login_required
from .. import db, socketio
from ..services import user_service

bp_chat = Blueprint("bp_chat", __name__)

@bp_chat.route("/api/friend_list")
@login_required
def get_friend_list():
    """Get friends list with last message info for messenger"""
    current_user_id = session["user_id"]
    friends = user_service.get_user_friends(current_user_id)

    # Enhance friends data with last message information
    friends_with_messages = []
    for friend in friends:
        friend_id = friend['id']

        # Find the messenger between current user and friend
        messenger = db.session.query(Messenger).filter(
            ((Messenger.first_user_id == current_user_id) & (Messenger.second_user_id == friend_id)) |
            ((Messenger.first_user_id == friend_id) & (Messenger.second_user_id == current_user_id))
        ).first()

        last_message = None
        last_message_time = None

        if messenger:
            # Get the last message in this conversation
            latest_msg = db.session.query(Message).filter(
                Message.messenger_id == messenger.id
            ).order_by(Message.created_at.desc()).first()

            if latest_msg:
                last_message = latest_msg.content
                last_message_time = latest_msg.created_at.strftime("%H:%M")

        friends_with_messages.append({
            'id': friend['id'],
            'username': friend['username'],
            'is_online': friend['is_online'],
            'last_message': last_message or 'No messages yet',
            'timestamp': last_message_time or '',
            'messenger_id': messenger.id if messenger else None
        })

    return jsonify(friends_with_messages)

@bp_chat.route("/api/messages/<int:friend_id>")
@login_required
def get_messages(friend_id):
    """Get all messages between current user and a friend"""
    current_user_id = session["user_id"]

    # Find the messenger between current user and friend
    messenger = db.session.query(Messenger).filter(
        ((Messenger.first_user_id == current_user_id) & (Messenger.second_user_id == friend_id)) |
        ((Messenger.first_user_id == friend_id) & (Messenger.second_user_id == current_user_id))
    ).first()

    if not messenger:
        # Create a new messenger if one doesn't exist
        messenger = Messenger(
            first_user_id=current_user_id,
            second_user_id=friend_id
        )
        db.session.add(messenger)
        db.session.commit()

    # Get all messages in this conversation
    messages_with_users = db.session.query(Message, User.username)\
                                   .join(User, Message.sender_id == User.id)\
                                   .filter(Message.messenger_id == messenger.id)\
                                   .order_by(Message.created_at.asc())\
                                   .all()

    messages_data = []
    for message, sender_username in messages_with_users:
        messages_data.append({
            "id": message.id,
            "sender_id": message.sender_id,
            "sender": sender_username,
            "content": message.content,
            "created_at": message.created_at.strftime("%H:%M")
        })

    # Get friend info
    friend = db.session.query(User).get(friend_id)

    return jsonify({
        'messages': messages_data,
        'messenger_id': messenger.id,
        'friend': {
            'id': friend.id,
            'username': friend.username,
            'is_online': friend.is_online
        }
    })

@bp_chat.route("/api/send_message", methods=['POST'])
@login_required
def send_message_api():
    """Send a message via JSON API"""
    current_user_id = session['user_id']
    data = request.get_json()

    friend_id = data.get('friend_id')
    content = data.get('content')

    if not friend_id or not content:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    friend = db.session.query(User).get(friend_id)
    if not friend:
        return jsonify({'success': False, 'message': 'Friend not found'}), 404

    # Find or create messenger
    messenger = db.session.query(Messenger).filter(
        ((current_user_id == Messenger.first_user_id) & (friend_id == Messenger.second_user_id)) |
        ((friend_id == Messenger.first_user_id) & (current_user_id == Messenger.second_user_id))
    ).first()

    if not messenger:
        messenger = Messenger(
            first_user_id=current_user_id,
            second_user_id=friend_id
        )
        db.session.add(messenger)
        db.session.flush()

    new_message = Message(
        sender_id=current_user_id,
        receiver_id=friend_id,
        messenger_id=messenger.id,
        content=content
    )
    db.session.add(new_message)
    db.session.commit()

    current_user = db.session.query(User).get(current_user_id)

    message_json = {
        'id': new_message.id,
        'content': new_message.content,
        'sender': current_user.username,
        'sender_id': current_user_id,
        'chat_id': messenger.id,
        'created_at': new_message.created_at.strftime("%H:%M")
    }

    socketio.emit("new_message", message_json, room=f'user_{friend_id}')
    socketio.emit("new_message", message_json, room=f'user_{current_user_id}')

    return jsonify({'success': True, 'message': message_json}), 200

