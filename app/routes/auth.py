from flask import Blueprint, redirect, url_for, request, session, jsonify, make_response
from ..services.user_service import UserServiceError
from ..services import user_service
import json

bp_auth = Blueprint("bp_auth", __name__)

@bp_auth.route('/api/signin', methods=['POST'])
def login():

    username = request.form['username']
    password = request.form['password']

    try:
        user = user_service.authenticate_user(username, password)

    except UserServiceError as error:
        return jsonify({'success': False, 'message': str(error)})
    
    session['user_id'] = user.id
    session['username'] = user.username

    print(request, session)
    return jsonify({"success": True})

@bp_auth.route('/api/signup', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    try: user_service.create_user(username, password)

    except UserServiceError as error:
        return jsonify({'success': False, 'message': str(error)})
    
    return jsonify({"success": True})

@bp_auth.route('/api/current_user')
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        user = user_service.get_user(session['user_id'])
        return jsonify({
            'id': user.id,
            'username': user.username,
            'display_name': user.display_name,
            'avatar_path': user.avatar_path,
            'bio': user.bio
        })
    except UserServiceError:
        return jsonify({'error': 'User not found'}), 404

@bp_auth.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('bp_auth.login'))