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
            # Get all posts with eager loading to avoid N+1 queries
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
        # Get all posts for this user with eager loading to avoid N+1 queries
        posts = db.session.query(Post, User.username)\
                          .join(User, Post.owner == User.id)\
                          .filter(User.username == username)\
                          .order_by(Post.created_at.desc())\
                          .limit(50)\
                          .all()

        return render_template('posts.html', username=session['username'], posts=posts, profile_user = username, current_user_id=session.get('user_id'))
    else:
        # User not found, redirect to 404 or home
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
        friends_query = get_friends_query(user.id).all()
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
        for friend, _friendship in friends_query:
            friend_socket_post_data = {
                "html": render_template("partials/post.html", username=session['username'], post_data=post_data, current_user_id=friend.id),
                "info": new_post.to_dict()
            }
            socketio.emit("new_post", friend_socket_post_data, room=f'user_{friend.id}')

        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully!',
            'post_id': new_post.id,
            'image_url': new_post.image_path
        }), 200

@bp_index.route('/delete_post', methods=['POST'])
@login_required
def delete_post():
    post_id = request.json.get('post_id')
    current_user_id = session['user_id']

    if not post_id:
        return jsonify({'success': False, 'message': 'Post ID required'}), 400

    # Find the post and verify ownership
    post = Post.query.filter_by(id=post_id, owner=current_user_id).first()
    if not post:
        return jsonify({'success': False, 'message': 'Post not found or not authorized'}), 404

    try:
        # Delete the image file from filesystem
        image_path = os.path.join('app', 'static', post.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)

        # Delete the post from database
        db.session.delete(post)
        db.session.commit()

        return jsonify({'success': True, 'message': 'Post deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error deleting post: {str(e)}'}), 500
