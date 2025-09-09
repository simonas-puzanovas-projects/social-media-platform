from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
socketio = SocketIO(app, cors_allowed_origins="*")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    
    sent_requests = db.relationship('Friendship', 
                                  foreign_keys='Friendship.requester_id',
                                  backref='requester', 
                                  lazy='dynamic')
    received_requests = db.relationship('Friendship', 
                                      foreign_keys='Friendship.requested_id',
                                      backref='requested', 
                                      lazy='dynamic')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic')

class Friendship(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    requested_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Friendship {self.requester_id} -> {self.requested_id} ({self.status})>'

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    data = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'type': self.type,
            'message': self.message,
            'data': json.loads(self.data) if self.data else None,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat()
        }

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# ============================================================================
# AUTH ROUTES
# ============================================================================

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists!', 'error')
            return render_template('login.html')
        
        password_hash = generate_password_hash(password)
        new_user = User(username=username, password_hash=password_hash)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ============================================================================
# MAIN DASHBOARD ROUTES
# ============================================================================

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session['username'])

@app.route('/friends')
@login_required
def friends():
    current_user_id = session['user_id']
    
    # Get accepted friends
    friends = get_friends_query(current_user_id).all()
    
    # Get received friend requests
    received_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requester_id
    ).filter(
        Friendship.requested_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    return render_template('friends.html', friends=friends, received_requests=received_requests)

# ============================================================================
# USER SEARCH & FRIEND REQUEST ROUTES
# ============================================================================

@app.route('/search_users')
@login_required
def search_users():
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    users = User.query.filter(
        User.username.contains(query),
        User.id != session['user_id']
    ).limit(10).all()
    
    current_user_id = session['user_id']
    results = []
    
    for user in users:
        status = get_friendship_status(current_user_id, user.id)
        results.append({
            'id': user.id,
            'username': user.username,
            'status': status
        })
    
    return jsonify(results)

@app.route('/send_friend_request', methods=['POST'])
@login_required
def send_friend_request():
    requested_user_id = request.json.get('user_id')
    current_user_id = session['user_id']
    
    if requested_user_id == current_user_id:
        return jsonify({'success': False, 'message': 'Cannot send friend request to yourself'})
    
    existing_friendship = find_friendship(current_user_id, requested_user_id)
    if existing_friendship:
        return jsonify({'success': False, 'message': 'Friendship already exists or pending'})
    
    new_friendship = Friendship(
        requester_id=current_user_id,
        requested_id=requested_user_id,
        status='pending'
    )
    
    db.session.add(new_friendship)
    db.session.commit()
    
    # Create notification for the requested user
    requester = User.query.get(current_user_id)
    create_notification(
        requested_user_id,
        'friend_request',
        f'{requester.username} sent you a friend request',
        {'friendship_id': new_friendship.id, 'requester_username': requester.username}
    )
    
    return jsonify({'success': True, 'message': 'Friend request sent!'})

@app.route('/respond_friend_request', methods=['POST'])
@login_required
def respond_friend_request():
    friendship_id = request.json.get('friendship_id')
    response = request.json.get('response')
    current_user_id = session['user_id']
    
    friendship = Friendship.query.filter_by(
        id=friendship_id,
        requested_id=current_user_id,
        status='pending'
    ).first()
    
    if not friendship:
        return jsonify({'success': False, 'message': 'Friend request not found'})
    
    if response == 'accept':
        friendship.status = 'accepted'
        db.session.commit()
        
        # Notify the requester that their request was accepted
        accepter = User.query.get(current_user_id)
        create_notification(
            friendship.requester_id,
            'friend_request_accepted',
            f'{accepter.username} accepted your friend request',
            {'friendship_id': friendship.id, 'accepter_username': accepter.username}
        )
        
        return jsonify({'success': True, 'message': 'Friend request accepted!'})
    elif response == 'reject':
        requester_id = friendship.requester_id
        
        # Delete any notifications related to this friend request
        related_notifications = Notification.query.filter_by(
            user_id=current_user_id,
            type='friend_request'
        ).all()
        
        for notification in related_notifications:
            data = clean_notification_data(notification.data)
            if data and data.get('friendship_id') == friendship_id:
                db.session.delete(notification)
        
        db.session.delete(friendship)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Friend request rejected'})
    
    return jsonify({'success': False, 'message': 'Invalid response'})

@app.route('/cancel_friend_request', methods=['POST'])
@login_required
def cancel_friend_request():
    friendship_id = request.json.get('friendship_id')
    current_user_id = session['user_id']
    
    friendship = Friendship.query.filter_by(
        id=friendship_id,
        requester_id=current_user_id,
        status='pending'
    ).first()
    
    if not friendship:
        return jsonify({'success': False, 'message': 'Friend request not found'})
    
    # Delete any notifications related to this friend request from the recipient's notifications
    related_notifications = Notification.query.filter_by(
        user_id=friendship.requested_id,
        type='friend_request'
    ).all()
    
    for notification in related_notifications:
        data = clean_notification_data(notification.data)
        if data and data.get('friendship_id') == friendship_id:
            db.session.delete(notification)
    
    # Delete the friendship request
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friend request cancelled'})

@app.route('/remove_friend', methods=['POST'])
@login_required
def remove_friend():
    friend_user_id = request.json.get('friend_user_id')
    current_user_id = session['user_id']
    
    if friend_user_id == current_user_id:
        return jsonify({'success': False, 'message': 'Cannot remove yourself'})
    
    # Find the friendship (could be either direction)
    friendship = find_friendship(current_user_id, friend_user_id, status='accepted')
    
    if not friendship:
        return jsonify({'success': False, 'message': 'Friendship not found'})
    
    # Delete the friendship
    db.session.delete(friendship)
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Friend removed successfully'})

# ============================================================================
# API ROUTES (JSON DATA)
# ============================================================================

@app.route('/api/friends')
@login_required
def get_friends_data():
    current_user_id = session['user_id']
    
    # Get accepted friends
    friends = get_friends_query(current_user_id).all()
    
    friends_data = []
    for user, friendship in friends:
        friends_data.append({
            'id': user.id,
            'username': user.username,
            'is_online': user.is_online,
            'last_seen': user.last_seen.isoformat() if user.last_seen else None
        })
    
    return jsonify(friends_data)

@app.route('/api/friend_requests')
@login_required
def get_friend_requests_data():
    current_user_id = session['user_id']
    
    # Get received friend requests
    received_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requester_id
    ).filter(
        Friendship.requested_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    requests_data = []
    for user, friendship in received_requests:
        requests_data.append({
            'id': user.id,
            'username': user.username,
            'friendship_id': friendship.id,
            'created_at': friendship.created_at.isoformat()
        })
    
    return jsonify(requests_data)

@app.route('/api/sent_requests')
@login_required
def get_sent_requests_data():
    current_user_id = session['user_id']
    
    # Get sent friend requests that are still pending
    sent_requests = db.session.query(User, Friendship).join(
        Friendship, User.id == Friendship.requested_id
    ).filter(
        Friendship.requester_id == current_user_id,
        Friendship.status == 'pending'
    ).all()
    
    requests_data = []
    for user, friendship in sent_requests:
        requests_data.append({
            'id': user.id,
            'username': user.username,
            'friendship_id': friendship.id,
            'created_at': friendship.created_at.isoformat()
        })
    
    return jsonify(requests_data)

# ============================================================================
# NOTIFICATION ROUTES
# ============================================================================

@app.route('/notifications')
@login_required
def get_notifications():
    current_user_id = session['user_id']
    notifications = Notification.query.filter_by(user_id=current_user_id).order_by(
        Notification.created_at.desc()
    ).limit(50).all()
    
    # Filter out invalid friend request notifications and clean them up
    valid_notifications = []
    notifications_to_delete = []
    
    for notification in notifications:
        if notification.type == 'friend_request':
            data = clean_notification_data(notification.data)
            if data:
                friendship_id = data.get('friendship_id')
                
                # Check if the friendship still exists and is pending
                friendship = Friendship.query.filter_by(
                    id=friendship_id,
                    requested_id=current_user_id,
                    status='pending'
                ).first()
                
                if friendship:
                    # Friendship is still valid and pending
                    valid_notifications.append(notification)
                else:
                    # Friendship doesn't exist or is no longer pending, mark for deletion
                    notifications_to_delete.append(notification)
            else:
                # Invalid notification data, mark for deletion
                notifications_to_delete.append(notification)
        else:
            # Not a friend request notification, include it
            valid_notifications.append(notification)
    
    # Clean up invalid notifications
    if notifications_to_delete:
        for notification in notifications_to_delete:
            db.session.delete(notification)
        db.session.commit()
    
    return jsonify([notification.to_dict() for notification in valid_notifications])

@app.route('/cleanup_notifications', methods=['POST'])
@login_required
def cleanup_notifications():
    """Clean up all stale friend request notifications for the current user"""
    current_user_id = session['user_id']
    notifications = Notification.query.filter_by(
        user_id=current_user_id,
        type='friend_request'
    ).all()
    
    deleted_count = 0
    for notification in notifications:
        data = clean_notification_data(notification.data)
        if data:
            friendship_id = data.get('friendship_id')
            
            # Check if the friendship still exists and is pending
            friendship = Friendship.query.filter_by(
                id=friendship_id,
                requested_id=current_user_id,
                status='pending'
            ).first()
            
            if not friendship:
                # Friendship doesn't exist or is no longer pending, delete notification
                db.session.delete(notification)
                deleted_count += 1
        else:
            # Invalid notification data, delete it
            db.session.delete(notification)
            deleted_count += 1
    
    if deleted_count > 0:
        db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Cleaned up {deleted_count} stale notifications'
    })

def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(username='admin').first():
            admin_user = User(
                username='admin',
                password_hash=generate_password_hash('password123')
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Created admin user: admin/password123")

# Socket event handlers
@socketio.on('connect')
def on_connect():
    if 'user_id' in session:
        user_id = session['user_id']
        join_room(f'user_{user_id}')
        
        # Update user online status
        user = User.query.get(user_id)
        if user:
            user.is_online = True
            user.last_seen = datetime.utcnow()
            db.session.commit()
        
        print(f'User {user_id} connected')

@socketio.on('disconnect')
def on_disconnect():
    if 'user_id' in session:
        user_id = session['user_id']
        leave_room(f'user_{user_id}')
        
        # Update user offline status
        user = User.query.get(user_id)
        if user:
            user.is_online = False
            user.last_seen = datetime.utcnow()
            db.session.commit()
        
        print(f'User {user_id} disconnected')

# Helper functions
def find_friendship(user1_id, user2_id, status=None):
    """Find friendship between two users (handles bidirectional relationship)"""
    query = Friendship.query.filter(
        ((Friendship.requester_id == user1_id) & (Friendship.requested_id == user2_id)) |
        ((Friendship.requester_id == user2_id) & (Friendship.requested_id == user1_id))
    )
    if status:
        query = query.filter(Friendship.status == status)
    return query.first()

def get_friendship_status(current_user_id, other_user_id):
    """Get friendship status between current user and another user"""
    friendship = find_friendship(current_user_id, other_user_id)
    
    if not friendship:
        return 'none'
    elif friendship.status == 'accepted':
        return 'friends'
    elif friendship.requester_id == current_user_id:
        return 'request_sent'
    else:
        return 'request_received'

def get_friends_query(current_user_id):
    """Get query for accepted friends of current user"""
    return db.session.query(User, Friendship).join(
        Friendship,
        (User.id == Friendship.requester_id) | (User.id == Friendship.requested_id)
    ).filter(
        Friendship.status == 'accepted',
        ((Friendship.requester_id == current_user_id) | (Friendship.requested_id == current_user_id)),
        User.id != current_user_id
    )

def clean_notification_data(notification_data_str):
    """Safely parse notification data JSON"""
    if not notification_data_str:
        return None
    try:
        return json.loads(notification_data_str)
    except (json.JSONDecodeError, TypeError):
        return None

def create_notification(user_id, notification_type, message, data=None):
    notification = Notification(
        user_id=user_id,
        type=notification_type,
        message=message,
        data=json.dumps(data) if data else None
    )
    db.session.add(notification)
    db.session.commit()
    
    # Emit real-time notification
    socketio.emit('new_notification', notification.to_dict(), room=f'user_{user_id}')
    return notification

if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0')