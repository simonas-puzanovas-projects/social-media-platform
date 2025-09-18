from flask import Blueprint, render_template, redirect, url_for, session
from .. import db
from ..models import User

bp_index = Blueprint("bp_index", __name__, template_folder="../templates")

@bp_index.route('/')
def index():
    if 'user_id' in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        if user:
            return render_template('home.html', username=session['username'])
        else:
            session.clear()

    return redirect(url_for('bp_auth.login'))