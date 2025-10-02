from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from werkzeug.utils import secure_filename
from .. import db, socketio
from ..models import User, Post
from ..decorators import login_required
from ..helpers import get_friends_query
import os

from ..services.user_service import UserServiceError
from ..services.post_service import PostServiceError
from ..services import user_service, post_service

bp_index = Blueprint("bp_index", __name__, template_folder="../templates")

@bp_index.route('/')
def index():
    if 'user_id' in session:
        user = User.query.filter_by(id=session["user_id"]).first()
        if user:
            posts = db.session.query(Post, User.username)\
                             .join(User, Post.owner == User.id)\
                             .order_by(Post.created_at.desc())\
                             .limit(50)\
                             .all()

            return render_template('posts.html', username=session['username'], posts=posts, current_user_id=session['user_id'])
        else:
            session.clear()

    return redirect(url_for('bp_auth.login'))

@bp_index.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first()
    if user:
        posts = db.session.query(Post, User.username)\
                          .join(User, Post.owner == User.id)\
                          .filter(User.username == username)\
                          .order_by(Post.created_at.desc())\
                          .limit(50)\
                          .all()

        return render_template('posts.html', username=session['username'], posts=posts, profile_user = username, current_user_id=session.get('user_id'))
    else:
        return redirect(url_for('bp_index.index'))


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
        post_data = db.session.query(Post, User.username)\
                            .join(User, Post.owner == User.id)\
                            .filter(Post.id == new_post.id)\
                            .first()

        # Send to post owner with delete button
        owner_socket_post_data = {
            "html": render_template("partials/post.html", username=session['username'], post_data=post_data, current_user_id=user.id),
            "info": new_post.to_dict()
        }
        socketio.emit("new_post", owner_socket_post_data, room=f'user_{user.id}')

        # Send to friends without delete button
        for friend in friends_query:
            friend_socket_post_data = {
                "html": render_template("partials/post.html", username=session['username'], post_data=post_data, current_user_id=friend["id"]),
                "info": new_post.to_dict()
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

