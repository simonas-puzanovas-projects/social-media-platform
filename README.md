# Social Media Platform

A comprehensive Flask-based social media platform with real-time messaging, image sharing, and social networking features.

## Project Overview

This is a full-featured web-based social media platform built with Flask that provides complete social networking functionality including user authentication, friend management, real-time chat messaging, image posting, and live notifications. The application leverages WebSocket connections for real-time communication and features a modern, responsive user interface.

## Current Features

### ✅ Authentication System
- User registration and login with secure password hashing
- Session management with login-required decorators
- Custom error handling for authentication failures
- Logout functionality with session cleanup

### ✅ User Management & Profiles
- User profiles with online status tracking
- Last seen timestamps and activity indicators
- Profile pages displaying user posts
- Real-time online/offline status updates

### ✅ Posts & Image Sharing
- **Image Upload System**: Upload images with drag-and-drop interface
- **Posts Feed**: Chronological timeline of all user posts
- **Image Processing**: Automatic image validation and resizing using Pillow
- **File Management**: Secure file storage with unique filenames
- **Post Management**: Delete your own posts with file cleanup
- **Profile Views**: View individual user profiles and their posts

### ✅ Friend System
- Send friend requests to other users
- Accept/reject incoming friend requests
- Cancel sent friend requests
- Remove existing friends
- Real-time friendship status updates
- Complete REST API endpoints for friend management
- Friend search with live results and status indicators

### ✅ Real-time Chat System
- **Direct Messaging**: Private chat between friends
- **Message History**: Persistent message storage and retrieval
- **Real-time Delivery**: Instant message delivery using WebSocket
- **Chat Interface**: Modern chat UI with message bubbles
- **Friend List**: Chat-specific friends list with online status
- **Message Threading**: Organized conversation threads

### ✅ Notifications System
- Real-time notification delivery using WebSocket
- Friend request notifications
- Chat message notifications
- Visual notification indicators and counters
- Toast notification system with auto-dismiss
- Notification cleanup for expired/invalid notifications

### ✅ Real-time Features
- WebSocket integration with Flask-SocketIO
- Live online/offline status updates
- Real-time message delivery
- Instant notification delivery
- Socket room management for private communications

## Technology Stack

- **Backend Framework**: Flask 3.0.0 (Python)
- **Database**: SQLite with SQLAlchemy 3.1.1 ORM
- **Real-time Communication**: Flask-SocketIO 5.3.6 for WebSocket connections
- **Image Processing**: Pillow 10.0.1 for image validation and processing
- **Security**: Werkzeug 3.0.1 for password hashing and secure filename handling
- **Configuration**: python-dotenv 1.0.0 for environment management
- **Frontend**: Vanilla HTML5, CSS3, JavaScript (ES6+)
- **UI/UX**: Custom responsive CSS with modern design patterns
- **File Storage**: Local filesystem with secure upload handling

## Database Models

### User
- **Core Fields**: ID, username, password_hash
- **Activity Tracking**: is_online, last_seen timestamps
- **Relationships**: Links to friendships, notifications, posts, and messages

### Friendship
- **Relationship Tracking**: requester_id, requested_id with foreign keys
- **Status Management**: pending/accepted status with timestamps
- **Bidirectional Support**: Handles mutual friendship connections

### Post
- **Content Management**: owner (user_id), image_path for uploaded images
- **Timestamps**: created_at, updated_at for post lifecycle
- **File Integration**: Links to physical image files in uploads directory

### Messenger
- **Chat Rooms**: first_user_id, second_user_id for private conversations
- **Message Threading**: Container for organizing message exchanges
- **Friend Integration**: Only friends can create messenger threads

### Message
- **Communication**: sender_id, receiver_id, content for message data
- **Threading**: messenger_id to group messages in conversations
- **History**: created_at timestamps for chronological ordering

### Notification
- **User Targeting**: user_id for notification delivery
- **Content**: type, message, JSON data for structured information
- **State Tracking**: is_read status and created_at timestamps

## File Structure

```
social-media-platform/
├── main.py                       # Application entry point with database initialization
├── requirements.txt              # Python dependencies (Flask, SocketIO, Pillow, etc.)
├── app/                          # Main application package
│   ├── __init__.py              # App factory, SocketIO, and database configuration
│   ├── config.py                # Application configuration management
│   ├── decorators.py            # Custom decorators (login_required, etc.)
│   ├── error_handlers.py        # Custom error page handlers
│   ├── models/                  # Database models
│   │   └── __init__.py          # User, Friendship, Post, Message, Messenger, Notification
│   ├── helpers/                 # Utility functions
│   │   ├── __init__.py          # Helper function exports
│   │   ├── chat.py              # Chat-related helper functions
│   │   ├── friends.py           # Friendship management helpers
│   │   └── notifications.py     # Notification system helpers
│   ├── routes/                  # Route blueprints
│   │   ├── __init__.py          # Blueprint registration
│   │   ├── auth.py              # Authentication (login/register/logout)
│   │   ├── index.py             # Home page, posts feed, image upload
│   │   ├── chat.py              # Real-time messaging and chat interface
│   │   ├── friends.py           # Friend management and search
│   │   └── notifications.py     # Notification delivery and cleanup
│   ├── socket/                  # WebSocket event handlers
│   │   └── __init__.py          # Socket.IO events for real-time features
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── index.html           # Base layout with navigation
│   │   ├── login.html           # Authentication page
│   │   ├── posts.html           # Posts feed and profile pages
│   │   ├── chat.html            # Chat interface and messaging
│   │   ├── friends.html         # Friends management interface
│   │   ├── sidebar.html         # Sidebar component template
│   │   ├── upload_image.html    # Image upload component
│   │   ├── notification_window.html # Notification window component
│   │   ├── toast_notification.html # Toast notification component
│   │   ├── partials/            # Reusable template components
│   │   └── errors/              # Custom error pages (404, 401, etc.)
│   └── static/                  # Static assets
│       ├── style.css            # Global styles and layout
│       ├── global.css           # Additional global styling
│       ├── sidebar.css          # Sidebar component styles
│       ├── login.css            # Authentication page styles
│       ├── posts.css            # Posts feed styling
│       ├── post.css             # Individual post component styles
│       ├── chat.css             # Chat interface styling
│       ├── friends.css          # Friends management styling
│       ├── errors.css           # Error page styling
│       ├── upload_image.css     # Image upload component styles
│       ├── index.js             # Core JavaScript with Socket.IO setup
│       ├── login.js             # Authentication page interactions
│       ├── posts.js             # Posts feed and image upload functionality
│       ├── upload_image.js      # Image upload functionality
│       ├── chat.js              # Real-time chat functionality
│       ├── friends.js           # Friends management interactions
│       ├── toast_notification.js # Toast notification system
│       └── uploads/             # User-uploaded image storage
└── instance/                    # Database and instance-specific files
```

## Application Routes & API Endpoints

### Authentication Routes (`bp_auth`)
- **`GET/POST /login`** - Login page and authentication handling
- **`POST /register`** - New user registration
- **`GET /logout`** - User logout and session cleanup

### Main Application Routes (`bp_index`)
- **`GET /`** - Home page with posts feed (redirects to login if not authenticated)
- **`GET /profile/<username>`** - User profile pages displaying individual user posts
- **`POST /upload_image`** - Image upload endpoint with validation and storage
- **`POST /delete_post`** - Delete user's own posts with file cleanup

### Chat System Routes (`bp_chat`)
- **`GET /chat`** - Main chat interface page
- **`GET /chat/friends_list`** - Get friends list for chat (returns HTML partial)
- **`GET /chat/open/<username>`** - Open chat conversation with specific friend
- **`POST /chat/send_message`** - Send real-time message to friend

### Friends Management Routes (`bp_friends`)
- **`GET /friends`** - Friends management interface page
- **`GET /search_users`** - Live user search with friendship status indicators
- **`POST /send_friend_request`** - Send friend request to another user
- **`POST /respond_friend_request`** - Accept or reject incoming friend requests
- **`POST /cancel_friend_request`** - Cancel previously sent friend requests
- **`POST /remove_friend`** - Remove existing friendship

### Friends API Endpoints (`bp_friends`)
- **`GET /api/friends`** - Get current user's friends list (JSON)
- **`GET /api/friend_requests`** - Get incoming friend requests (JSON)
- **`GET /api/sent_requests`** - Get sent friend requests (JSON)

### Notifications System (`bp_notifications`)
- **`GET /notifications`** - Retrieve user notifications (JSON)
- **`POST /cleanup_notifications`** - Clean up expired/invalid notifications

### WebSocket Events (Real-time)
- **`connect`** - User connection with online status update
- **`disconnect`** - User disconnection with offline status
- **`new_message`** - Real-time message delivery to chat recipients
- **`friend_request_sent`** - Live friend request notifications
- **`notification_update`** - Real-time notification delivery

## Setup & Installation

### Prerequisites
- Python 3.8+ (recommended: Python 3.11+)
- pip (Python package manager)

### Installation Steps

1. **Clone or Download** the project to your local machine

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Environment Configuration** (optional)
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file to configure your environment variables if needed. The application will work with default settings.

6. **Create Upload Directory** (for image uploads)
   ```bash
   mkdir -p app/static/uploads
   ```

7. **Run Application**
   ```bash
   python main.py
   ```

   The application will:
   - Automatically create the SQLite database
   - Set up all required tables (User, Friendship, Post, Message, etc.)
   - Create a default admin user (`admin` / `password123`)

8. **Access Application**
   - Open your browser to: `http://localhost:5000` or `http://127.0.0.1:5000`
   - Register a new account or use the admin credentials

### Configuration Notes

- **Database**: SQLite database will be created automatically in the `instance/` directory
- **File Uploads**: Images are stored in `app/static/uploads/` with unique filenames
- **Real-time Features**: WebSocket connections handled automatically by Flask-SocketIO
- **Security**: Passwords are hashed using Werkzeug's secure methods

### Environment Variables (.env file)

The application supports the following environment variables for configuration:

- **SECRET_KEY**: Flask secret key for session security (default: auto-generated)
- **FLASK_ENV**: Environment mode (default: `development`)
- **FLASK_DEBUG**: Debug mode toggle (default: `True`)
- **DATABASE_URL**: Database connection string (default: `sqlite:///users.db`)
- **CORS_ALLOWED_ORIGINS**: Comma-separated list of allowed CORS origins
- **UPLOAD_FOLDER**: Directory for file uploads (default: `app/static/uploads`)
- **MAX_CONTENT_LENGTH**: Maximum file upload size in bytes (default: 10MB)

### Default Admin Account
- **Username**: `admin`
- **Password**: `password123`
- Created automatically on first run

## Usage Guide

### Getting Started
1. **Register** a new account or login with existing credentials
2. **Search for users** using the friends management page
3. **Send friend requests** to connect with other users
4. **Upload images** from the main posts feed using the upload button
5. **Start chatting** with friends through the real-time messaging system

### Key Features
- **Posts Feed**: View chronological timeline of all user posts
- **Profile Pages**: Click on usernames to view individual profiles
- **Friend Management**: Send, accept, reject, and manage friend connections
- **Real-time Chat**: Instant messaging with online friends
- **Notifications**: Live updates for friend requests and messages
- **Image Sharing**: Upload and share images with automatic processing