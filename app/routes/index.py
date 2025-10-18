from flask import Blueprint, session, request, jsonify, redirect
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

@bp_index.route('/api/posts')
@login_required
def get_posts():
    try:
        user = user_service.get_user(session['user_id'])
        posts = post_service.query_posts()
        return jsonify({
            'success': True,
            'posts': posts,
            'current_user_id': session.get('user_id'),
            'current_username': user.username
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp_index.route('/api/profile/<username>')
@login_required
def profile(username):
    try:
        user = user_service.get_user_by_name(username)
        current_user = user_service.get_user(session['user_id'])
        posts = post_service.query_posts(profile_user_id=int(user.id))

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 404

    return jsonify({
        'success': True,
        'username': username,
        'posts': posts,
        'current_user_id': session.get('user_id'),
        'current_username': current_user.username
    })


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
            "post_data": new_post.to_dict(),
            "owner": user.username,
            "post_id": new_post.id,
            "current_user_id": user.id
        }
        socketio.emit("new_post", owner_socket_post_data, room=f'user_{user.id}')

        # Send to friends without delete button
       # for friend in friends_query:
       #     friend_socket_post_data = {
       #         "post_data": new_post.to_dict(),
       #         "owner": user.username,
       #         "post_id": new_post.id,
       #         "current_user_id": friend["id"]
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
        user_id = session["user_id"]

        post_service.delete_post(user_id, post_id)

        # Emit socket event to all users
        socketio.emit('post_deleted', {
            'post_id': post_id,
            'deleted_by': user_id
        })

        return jsonify({'success': True, 'message': 'Post deleted successfully'}), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 404

@bp_index.route("/api/like_post/<post_id>", methods=["POST"])
@login_required
def like_post(post_id):
    try:
        post_likes = post_service.query_post_likes(post_id)
        user_id = session["user_id"]
        user = user_service.get_user(user_id)

        #unlike if already liked
        for like in post_likes:
            if like.user_id == user_id:
                post_service.remove_like(like.id)
                new_count = len(post_likes) - 1

                # Emit socket event for unlike
                socketio.emit('post_unliked', {
                    'post_id': int(post_id),
                    'like_count': new_count,
                    'user_id': user_id
                })

                return f'{new_count}'

        post_service.create_like(user_id, post_id)
        new_count = len(post_likes) + 1

        # Emit socket event for like
        socketio.emit('post_liked', {
            'post_id': int(post_id),
            'like_count': new_count,
            'user_id': user_id,
            'username': user.username
        })

        return f'{new_count}'

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 404

@bp_index.route("/api/comment/<int:post_id>", methods=["POST"])
@login_required
def create_comment(post_id):
    try:
        content = request.form.get('comment') or request.json.get('comment')
        parent_id = request.form.get('parent_id') or request.json.get('parent_id')  # For replies

        if parent_id:
            parent_id = int(parent_id)

        new_comment = post_service.create_comment(
            user_id=session['user_id'],
            post_id=post_id,
            content=content,
            parent_id=parent_id
        )

        # Get updated comment count
        comment_count = post_service.get_comment_count(post_id)

        # Emit socket event for new comment
        # Include author_user_id so frontend can filter out duplicates
        socketio.emit('post_commented', {
            'post_id': post_id,
            'comment': new_comment.to_dict(),
            'comment_count': comment_count,
            'is_reply': bool(parent_id),
            'author_user_id': session['user_id']
        })

        # Return comment data as JSON
        return jsonify({
            'success': True,
            'comment': new_comment.to_dict(),
            'is_reply': bool(parent_id)
        })

    except PostServiceError as e:
        return jsonify({'success': False, 'message': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to post comment'}), 500

@bp_index.route("/api/comments/<int:post_id>", methods=["GET"])
@login_required
def get_comments(post_id):
    try:
        comments = post_service.get_post_comments(post_id)
        return jsonify({
            'success': True,
            'comments': [comment.to_dict() for comment in comments],
            'post_id': post_id,
            'current_user_id': session['user_id']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to load comments'}), 500

@bp_index.route("/api/comment/<int:comment_id>", methods=["DELETE"])
@login_required
def delete_comment(comment_id):
    try:
        # Get comment info before deletion
        from ..models import PostComment
        comment = PostComment.query.get(comment_id)
        if not comment:
            return jsonify({'success': False, 'message': 'Comment not found'}), 404

        post_id = comment.post_id

        # Delete the comment
        post_service.delete_comment(session['user_id'], comment_id)

        # Get updated comment count
        comment_count = post_service.get_comment_count(post_id)

        # Emit socket event for comment deletion
        socketio.emit('post_comment_deleted', {
            'post_id': post_id,
            'comment_id': comment_id,
            'comment_count': comment_count
        })

        return jsonify({'success': True}), 200
    except PostServiceError as e:
        return jsonify({'success': False, 'message': str(e)}), 403
    except Exception as e:
        return jsonify({'success': False, 'message': 'Failed to delete comment'}), 500

@bp_index.route("/api/comment_count/<int:post_id>", methods=["GET"])
@login_required
def get_comment_count(post_id):
    """Return just the comment count for HTMX swap"""
    try:
        count = post_service.get_comment_count(post_id)
        return f'💬 {count}'
    except Exception as e:
        return '💬 0'


