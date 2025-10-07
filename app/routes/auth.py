from flask import Blueprint, render_template, redirect, url_for, request, session, jsonify
from ..services.user_service import UserServiceError
from ..services import user_service

bp_auth = Blueprint("bp_auth", __name__, template_folder = "../templates")

@bp_auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user = user_service.authenticate_user(username, password)

        except UserServiceError as error:
            return jsonify({'success': False, 'message': str(error)})
        
        session['user_id'] = user.id
        session['username'] = user.username

        return redirect(url_for('bp_index.index'))
    
    if 'user_id' in session:
        return redirect(url_for("bp_index.index"))

    return render_template('login.html')

@bp_auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            user_service.create_user(username, password)

        except UserServiceError as error:
            return jsonify({'success': False, 'message': str(error)})

        return redirect(url_for('bp_auth.login'))
    
    return render_template('login.html')

@bp_auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp_auth.login'))