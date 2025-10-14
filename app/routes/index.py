from flask import Blueprint, render_template, session, request, jsonify, redirect
from .. import socketio
from ..decorators import login_required
import os

from ..services.user_service import UserServiceError
from ..services.post_service import PostServiceError
from ..services import user_service, post_service

bp_index = Blueprint("bp_index", __name__)

@bp_index.route('/')
@login_required
def index():
    return jsonify({"success": True})

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
        owner_socket_post_data = {
            "html": render_template("partials/post.html", username=session['username'], post_data=new_post.to_dict(), current_user_id=user.id),
            "owner": user.username,
            "post_id": new_post.id
        }
        socketio.emit("new_post", owner_socket_post_data, room=f'user_{user.id}')

        # Send to friends without delete button
       # for friend in friends_query:
       #     friend_socket_post_data = {
       #         "html": render_template("partials/post.html", username=session['username'], post_data=new_post.to_dict(), current_user_id=friend["id"]),
       #         "owner": user.username,
       #         "post_id": new_post.id
       #     }
       #     socketio.emit("new_post", friend_socket_post_data, room=f'user_{friend["id"]}')

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
        return jsonify({'success': False, 'message': str(e)}), 404

@bp_index.route("/api/like_post/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    try:
        post_likes = post_service.query_post_likes(post_id)

        #unlike if already liked
        for like in post_likes:
            if like.user_id == session["user_id"]:
                post_service.remove_like(like.id)
                return f'{len(post_likes)-1}'

        post_service.create_like(session["user_id"], post_id)
        return f'{len(post_likes)+1}'

    except Exception as e:
        return jsonify({'success': False, 'message': e}), 404

@bp_index.route("/api/comment/<int:post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    try:
        content = request.form.get('comment')
        parent_id = request.form.get('parent_id')  # For replies

        if parent_id:
            parent_id = int(parent_id)

        new_comment = post_service.create_comment(
            user_id=session['user_id'],
            post_id=post_id,
            content=content,
            parent_id=parent_id
        )

        # If this is a reply to a comment, return just the single reply HTML
        if parent_id:
            return render_template('partials/single_reply.html',
                                 reply=new_comment,
                                 post_id=post_id,
                                 parent_id=parent_id,
                                 current_user_id=session['user_id'])

        # Otherwise return all comments HTML for this post
        comments = post_service.get_post_comments(post_id)
        comment_count = post_service.get_comment_count(post_id)

        return render_template('partials/comments.html',
                             comments=comments,
                             post_id=post_id,
                             current_user_id=session['user_id'],
                             username=session['username'])

    except PostServiceError as e:
        return f'<div class="error-message">{str(e)}</div>', 400
    except Exception as e:
        return f'<div class="error-message">Failed to post comment</div>', 500

@bp_index.route("/api/comments/<int:post_id>", methods=["GET"])
@login_required
def get_comments(post_id):
    try:
        comments = post_service.get_post_comments(post_id)
        return render_template('partials/comments.html',
                             comments=comments,
                             post_id=post_id,
                             current_user_id=session['user_id'],
                             username=session['username'])
    except Exception as e:
        return f'<div class="error-message">Failed to load comments</div>', 500

@bp_index.route("/api/comment/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    try:
        post_service.delete_comment(session['user_id'], comment_id)
        return '', 200  # HTMX will remove the element
    except PostServiceError as e:
        return f'<div class="error-message">{str(e)}</div>', 403
    except Exception as e:
        return f'<div class="error-message">Failed to delete comment</div>', 500

@bp_index.route("/api/comment_count/<int:post_id>", methods=["GET"])
@login_required
def get_comment_count(post_id):
    """Return just the comment count for HTMX swap"""
    try:
        count = post_service.get_comment_count(post_id)
        return f'💬 {count}'
    except Exception as e:
        return '💬 0'


