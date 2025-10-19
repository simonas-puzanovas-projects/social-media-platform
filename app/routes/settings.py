from flask import Blueprint, request, session, jsonify
from ..services.user_settings_service import UserSettingsServiceError
from ..services import user_settings_service

bp_settings = Blueprint("bp_settings", __name__)

def require_auth():
    """Helper to check if user is authenticated"""
    if 'user_id' not in session:
        return None
    return session['user_id']

@bp_settings.route('/api/user/settings', methods=['GET'])
def get_settings():
    """Get current user settings"""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        settings = user_settings_service.get_user_settings(user_id)
        return jsonify({'success': True, 'settings': settings})

    except UserSettingsServiceError as error:
        return jsonify({'success': False, 'message': str(error)}), 400

@bp_settings.route('/api/user/profile', methods=['POST'])
def update_profile():
    """Update user profile (display name and bio)"""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        data = request.get_json() or {}
        display_name = data.get('display_name')
        bio = data.get('bio')

        settings = user_settings_service.update_profile(
            user_id=user_id,
            display_name=display_name,
            bio=bio
        )

        return jsonify({'success': True, 'settings': settings})

    except UserSettingsServiceError as error:
        return jsonify({'success': False, 'message': str(error)}), 400

@bp_settings.route('/api/user/password', methods=['POST'])
def change_password():
    """Change user password"""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        data = request.get_json() or {}
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not old_password or not new_password:
            return jsonify({'success': False, 'message': 'Both old and new passwords are required'}), 400

        user_settings_service.change_password(
            user_id=user_id,
            old_password=old_password,
            new_password=new_password
        )

        return jsonify({'success': True, 'message': 'Password changed successfully'})

    except UserSettingsServiceError as error:
        return jsonify({'success': False, 'message': str(error)}), 400

@bp_settings.route('/api/user/avatar', methods=['POST'])
def upload_avatar():
    """Upload user avatar"""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'message': 'No file uploaded'}), 400

        file = request.files['avatar']

        avatar_path = user_settings_service.upload_avatar(
            user_id=user_id,
            file=file
        )

        return jsonify({'success': True, 'avatar_path': avatar_path})

    except UserSettingsServiceError as error:
        return jsonify({'success': False, 'message': str(error)}), 400

@bp_settings.route('/api/user/account', methods=['DELETE'])
def delete_account():
    """Delete user account"""
    user_id = require_auth()
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401

    try:
        data = request.get_json() or {}
        password = data.get('password')

        if not password:
            return jsonify({'success': False, 'message': 'Password is required'}), 400

        user_settings_service.delete_account(
            user_id=user_id,
            password=password
        )

        # Clear session after account deletion
        session.clear()

        return jsonify({'success': True, 'message': 'Account deleted successfully'})

    except UserSettingsServiceError as error:
        return jsonify({'success': False, 'message': str(error)}), 400
