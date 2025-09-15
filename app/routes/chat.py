from flask import Blueprint, render_template, redirect, url_for, session, json
from ..helpers import get_friendship_status, find_friendship, create_notification, clean_notification_data, get_friends_query

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
@bp_chat.route("/chat/send_message")
def send_message():
    current_user_id = session['user_id']
    message = session.request.form["message"]
    friends_list = get_friends_query(current_user_id).all()
    friends_data = []

    for user, friendship in friends_list:
        friends_data.append({
            'id': user.id,
            'username': user.username,
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None
        })

@bp_chat.route("/chat/open/<username>")
def open_chat(username):
    current_user_id = session['user_id']
    friends_list = get_friends_query(current_user_id).all()
    friends_data = []

    for user, friendship in friends_list:
        if user.username == username:
            return render_template("partials/chat_messenger_chat.html", username = user.username)


