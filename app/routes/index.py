from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify, flash
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image
from .. import db
from ..models import User, Post
from ..decorators import login_required

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

            return render_template('home.html', username=session['username'], posts=posts)
        else:
            session.clear()

    return redirect(url_for('bp_auth.login'))

@bp_index.route('/upload_image', methods=['POST'])
@login_required
def upload_image():
    user = User.query.filter_by(id=session["user_id"]).first()
    if not user:
        return jsonify({'success': False, 'message': 'User not found'}), 404

    if 'image' not in request.files:
        return jsonify({'success': False, 'message': 'No image file provided'}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    # Validate file type
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if not file.filename.lower().endswith(tuple(allowed_extensions)):
        return jsonify({'success': False, 'message': 'Invalid file type. Only images allowed.'}), 400

    try:
        # Validate image by opening it
        img = Image.open(file.stream)
        img.verify()
        file.stream.seek(0)  # Reset stream after verification

        # Check image size (max 10MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({'success': False, 'message': 'File too large. Maximum size is 10MB.'}), 400

        # Create uploads directory if it doesn't exist
        upload_folder = os.path.join('app', 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)

        # Generate unique filename
        file_extension = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{uuid.uuid4().hex}.{file_extension}"
        file_path = os.path.join(upload_folder, unique_filename)

        # Save the file
        file.save(file_path)

        # Create database record
        new_post = Post(
            owner=user.id,
            image_path=f"uploads/{unique_filename}"
        )
        db.session.add(new_post)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Image uploaded successfully!',
            'post_id': new_post.id,
            'image_url': f"/static/uploads/{unique_filename}"
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error processing image: {str(e)}'}), 500

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
