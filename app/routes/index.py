from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from werkzeug.utils import secure_filename
from .. import db, socketio
from ..models import User, Post
from ..decorators import login_required
from ..services import friendship_service
import os

from ..services.user_service import UserServiceError
from ..services.post_service import PostServiceError
from ..services import user_service, post_service

bp_index = Blueprint("bp_index", __name__, template_folder="../templates")

@bp_index.route('/')
@login_required
def index():
    #posts = db.session.query(Post)\
    #                    .order_by(Post.created_at.desc())\
    #                    .limit(50)\
    #                    .all()
    #posts_dict = [post.to_dict() for post in posts]
    posts = post_service.query_posts()

    return render_template('posts.html', username=session['username'], posts=posts, current_user_id=session['user_id'])

@bp_index.route('/profile/<username>')
@login_required
def profile(username):
    try:
        user = user_service.get_user_by_name(username)
        posts = post_service.query_posts(profile_user_id=int(user.id))
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 404

    return render_template('posts.html', username=session['username'], posts=posts, profile_user = username, current_user_id=session.get('user_id'))


@bp_index.route('/upload_image', methods=['POST'])
@login_required
def upload_image():

        if 'image' not in request.files:
            return jsonify({'success': False, 'message': 'No image file provided'}), 400

        try:
            user = user_service.get_user(session['user_id'])
            file = post_service.validate_image(request.files["image"])
            new_post = post_service.create_post(user.id, file)

        except PostServiceError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        except UserServiceError as e:
            return jsonify({'success': False, 'message': str(e)}), 400

        #future pub/sub
        friends_query = user_service.get_user_friends(user.id)
        #post_data = db.session.query(Post)\
        #                    .join(User, Post.owner == User.id)\
        #                    .filter(Post.id == new_post.id)\
        #                    .first()

        # Send to post owner with delete button
        owner_socket_post_data = {
            "html": render_template("partials/post.html", username=session['username'], post_data=new_post.to_dict(), current_user_id=user.id),
            "owner": user.username
        }
        socketio.emit("new_post", owner_socket_post_data, room=f'user_{user.id}')

        # Send to friends without delete button
        for friend in friends_query:
            friend_socket_post_data = {
                "html": render_template("partials/post.html", username=session['username'], post_data=new_post.to_dict(), current_user_id=friend["id"]),
                "owner": user.username
            }
            socketio.emit("new_post", friend_socket_post_data, room=f'user_{friend["id"]}')

        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully!',
            'post_id': new_post.id,
            'image_url': new_post.image_path
        }), 200

@bp_index.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
    try:
        post_id = request.json.get('post_id')
        post_service.delete_post(session["user_id"], post_id)
        return jsonify({'success': True, 'message': 'Post deleted successfully'}), 200
    
    except Exception as e:
        return jsonify({'success': False, 'message': e}), 404

