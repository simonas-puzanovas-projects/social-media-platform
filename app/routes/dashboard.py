from flask import Blueprint, render_template, redirect, url_for, request, session, flash
from ..helpers import get_friends_query
from ..models import Friendship, User
from .. import db

bp_dashboard = Blueprint("bp_dashboard", __name__, template_folder="../templates")


@bp_dashboard.route('/friends')
#@login_required
def friends():
    current_user_id = session['user_id']
    
    # Get accepted friends
    friends = get_friends_query(current_user_id).all()
    
    # Get received friend requests
    received_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requester_id
    ).filter(
        Friendship.requested_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    return render_template('friends.html', friends=friends, received_requests=received_requests)