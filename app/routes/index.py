from flask import Blueprint, render_template, redirect, url_for, session

bp_index = Blueprint("bp_index", __name__, template_folder="../templates")

@bp_index.route('/')
def index():
    if 'user_id' in session:
        return render_template('home.html', username=session['username'])
    return redirect(url_for('bp_auth.login'))