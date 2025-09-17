from flask import Blueprint, render_template, redirect, url_for, session, json, request
from ..helpers import get_friendship_status, find_friendship, create_notification, clean_notification_data, get_friends_query, get_user_messenger
from ..models import Messenger, Message, Friendship, User
from .. import db, socketio

bp_chat = Blueprint("bp_chat", __name__, template_folder="../templates")

@bp_chat.route("/chat")
def chat():
    return render_template('chat.html')

@bp_chat.route("/chat/friends_list")
def get_friends_list():
    current_user_id = session['user_id']
    friends_list = get_friends_query(current_user_id).all()
    friends_data = []

    for user, friendship in friends_list:
        friends_data.append({
            'id': user.id,
            'username': user.username,
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None
        })

    return render_template("partials/chat_friends_list.html", friends=friends_data)

@bp_chat.route("/chat/send_message", methods=['POST'])
def send_message():
    current_user_id = session['user_id']
    friend_id = db.session.query(User).filter(User.username == request.form.get("friend_username")).first().id

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
def open_chat(username):

    current_user_id = session['user_id']
    friend_id = 0

    friends_list = get_friends_query(current_user_id).all()
    for friend, friendship in friends_list:
        if username == friend.username:
            friend_id = friend.id

    messenger = db.session.query(Messenger).filter(
        ((current_user_id == Messenger.first_user_id) & (friend_id == Messenger.second_user_id)) |
        ((friend_id == Messenger.first_user_id) & (current_user_id == Messenger.second_user_id))
        ).first()
    
    if messenger:
        messages = db.session.query(Message).filter(messenger.id == Message.messenger_id).all()
        print("found")

        json_data = []

        for message in messages:
            sender = db.session.query(User).filter(User.id == message.sender_id).first()

            if sender:
                json_data.append({
                    "sender": sender.username,
                    "content": message.content
                })

            else: print("friends name not found")

        return render_template("partials/chat_messenger_chat.html", username = username, messages = json_data)
    print("not found")


