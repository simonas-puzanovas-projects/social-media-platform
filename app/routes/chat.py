from flask import Blueprint, render_template, redirect, url_for, session, json, request
from ..helpers import create_notification, clean_notification_data
from ..models import Messenger, Message, Friendship, User
from ..decorators import login_required
from .. import db, socketio
from ..services import user_service

bp_chat = Blueprint("bp_chat", __name__, template_folder="../templates")

@bp_chat.route("/chat")
@login_required
def chat():
    return render_template('chat.html')

@bp_chat.route("/chat/friends_list")
@login_required

def get_friends_list():
    friends_data = user_service.get_user_friends(session["user_id"])

    return render_template("partials/chat_friends_list.html", friends=friends_data)

@bp_chat.route("/chat/send_message", methods=['POST'])
@login_required

def send_message():
    current_user_id = session['user_id']
    friend = db.session.query(User).filter(User.username == request.form.get("friend_username")).first()

    if not friend:
        return jsonify({'success': False, 'message': 'Friend not found'}), 404

    friend_id = friend.id

    messenger = db.session.query(Messenger).filter(
        (current_user_id == Messenger.first_user_id) & (friend_id == Messenger.second_user_id) |
        (friend_id == Messenger.first_user_id) & (current_user_id == Messenger.second_user_id)
        ).first()

    new_message = Message(
        sender_id = current_user_id,
        receiver_id = friend_id,
        messenger_id = messenger.id,
        content = request.form.get("content")
    )
    db.session.add(new_message)
    db.session.commit()

    message_json = {
        'content': new_message.content,
        'sender': db.session.query(User).get(session["user_id"]).username
    }

    socketio.emit("new_message", message_json, room=f'user_{friend_id}')

    return render_template("partials/message.html", message = message_json)

@bp_chat.route("/chat/open/<username>")
@login_required
def open_chat(username):

    friend_id = 0
    current_user_id = session["user_id"]

    friends_list = user_service.get_user_friends(session["user_id"])

    for friend in friends_list:
        if username == friend["username"]:
            friend_id = friend["id"]

    messenger = db.session.query(Messenger).filter(
        (current_user_id == Messenger.first_user_id) & (friend_id == Messenger.second_user_id) |
        (friend_id == Messenger.first_user_id) & (current_user_id == Messenger.second_user_id)
        ).first()
    
    if messenger:
        # Optimize with a single query using JOIN to avoid N+1 problem
        messages_with_users = db.session.query(Message, User.username)\
                                       .join(User, Message.sender_id == User.id)\
                                       .filter(Message.messenger_id == messenger.id)\
                                       .order_by(Message.created_at.asc())\
                                       .all()

        json_data = []
        for message, sender_username in messages_with_users:
            json_data.append({
                "sender": sender_username,
                "content": message.content
            })

        return render_template("partials/chat_messenger.html", username = username, messages = json_data)


