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

### Backend
- **Backend Framework**: Flask 3.0.0 (Python)
- **Database**: SQLite with SQLAlchemy 3.1.1 ORM
- **Real-time Communication**: Flask-SocketIO 5.3.6 for WebSocket connections
- **Image Processing**: Pillow 10.0.1 for image validation and processing
- **Security**: Werkzeug 3.0.1 for password hashing and secure filename handling
- **Configuration**: python-dotenv 1.0.0 for environment management
- **File Storage**: Local filesystem with secure upload handling

### Frontend
- **Framework**: SvelteKit 2.43.2 with Svelte 5
- **Build Tool**: Vite 7.1.7
- **Styling**: TailwindCSS 4.1.13
- **Language**: TypeScript 5.9.2
- **Real-time**: Socket.IO Client 4.8.1
- **Linting**: ESLint 9 with Svelte plugin

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
├── app/                          # Backend Flask application
│   ├── __init__.py              # App factory, SocketIO, and database configuration
│   ├── config.py                # Application configuration management
│   ├── decorators.py            # Custom decorators (login_required, etc.)
│   ├── error_handlers.py        # JSON error response handlers
│   ├── models/                  # Database models
│   │   └── __init__.py          # User, Friendship, Post, Message, Messenger, Notification
│   ├── helpers/                 # Utility functions
│   │   ├── __init__.py          # Helper function exports
│   │   ├── chat.py              # Chat-related helper functions
│   │   ├── friends.py           # Friendship management helpers
│   │   └── notifications.py     # Notification system helpers
│   ├── routes/                  # REST API route blueprints
│   │   ├── __init__.py          # Blueprint registration
│   │   ├── auth.py              # Authentication API (login/register/logout)
│   │   ├── index.py             # Posts API (feed, upload, comments)
│   │   ├── chat.py              # Chat API (messages, conversations)
│   │   ├── friends.py           # Friends API (search, requests, management)
│   │   └── notifications.py     # Notifications API (delivery, cleanup)
│   ├── services/                # Business logic services
│   │   ├── __init__.py          # Service initialization
│   │   ├── user_service.py      # User management logic
│   │   ├── post_service.py      # Post and comment logic
│   │   ├── friendship_service.py # Friendship logic
│   │   └── notification_service.py # Notification logic
│   ├── sockets/                 # WebSocket event handlers
│   │   └── __init__.py          # Socket.IO events for real-time features
│   └── static/                  # Static file storage
│       └── uploads/             # User-uploaded image storage
├── frontend/                     # SvelteKit frontend application
│   ├── src/
│   │   ├── routes/              # SvelteKit routes and pages
│   │   ├── lib/
│   │   │   └── components/      # Svelte UI components
│   │   ├── app.html             # HTML shell
│   │   └── app.css              # Global styles
│   ├── static/                  # Static assets
│   ├── package.json             # Node dependencies
│   ├── svelte.config.js         # SvelteKit configuration
│   ├── tailwind.config.js       # Tailwind CSS configuration
│   └── vite.config.ts           # Vite build configuration
└── instance/                    # Database and instance-specific files
```

## API Endpoints

All endpoints return JSON responses. The Flask backend serves as a REST API for the Svelte frontend.

### Authentication API (`bp_auth`)
- **`POST /api/signin`** - Authenticate user and create session
- **`POST /api/signup`** - Register new user account
- **`GET /api/current_user`** - Get currently authenticated user info
- **`GET /logout`** - Clear session and logout user

### Posts & Comments API (`bp_index`)
- **`GET /`** - Health check endpoint (requires authentication)
- **`GET /api/profile/<username>`** - Get user profile and their posts (JSON)
- **`POST /upload_image`** - Upload image post with validation
- **`POST /delete_post`** - Delete user's own post with file cleanup
- **`POST /api/like_post/<post_id>`** - Like/unlike a post, returns updated count
- **`POST /api/comment/<post_id>`** - Create comment or reply on a post
- **`GET /api/comments/<post_id>`** - Get all comments for a post
- **`DELETE /api/comment/<comment_id>`** - Delete user's own comment
- **`GET /api/comment_count/<post_id>`** - Get comment count for a post

### Chat & Messaging API (`bp_chat`)
- **`GET /api/friend_list`** - Get friends list with last message info for messenger
- **`GET /api/messages/<friend_id>`** - Get all messages with a friend (marks as read)
- **`POST /api/send_message`** - Send message to friend (JSON body: friend_id, content)

### Friends Management API (`bp_friends`)
- **`GET /search_users?q=<query>`** - Search users with friendship status
- **`POST /send_friend_request`** - Send friend request (JSON body: user_id)
- **`POST /respond_friend_request`** - Accept/reject request (JSON body: friendship_id, response)
- **`POST /cancel_friend_request`** - Cancel sent request (JSON body: friendship_id)
- **`POST /remove_friend`** - Remove existing friendship (JSON body: friend_user_id)
- **`GET /api/friends`** - Get current user's accepted friends list
- **`GET /api/friend_requests`** - Get incoming friend requests
- **`GET /api/sent_requests`** - Get sent pending friend requests

### Notifications API (`bp_notifications`)
- **`GET /notifications`** - Get user notifications with auto-cleanup
- **`POST /cleanup_notifications`** - Manually clean up stale notifications

### WebSocket Events (Real-time)
- **`connect`** - User connection with online status update
- **`disconnect`** - User disconnection with offline status
- **`new_message`** - Real-time message delivery to chat recipients
- **`friend_request_sent`** - Live friend request notifications
- **`notification_update`** - Real-time notification delivery

## Setup & Installation

### Prerequisites
- Python 3.8+ (recommended: Python 3.11+)
- Node.js 18+ and npm (for frontend)
- pip (Python package manager)

### Installation Steps

#### Backend Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd social-media-platform
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   ```

3. **Activate Virtual Environment**
   - **Windows**: `venv\Scripts\activate`
   - **Linux/Mac**: `source venv/bin/activate`

4. **Install Python Dependencies**
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

7. **Run Backend Server**
   ```bash
   python main.py
   ```

   The application will:
   - Automatically create the SQLite database
   - Set up all required tables (User, Friendship, Post, Message, etc.)
   - Create a default admin user (`admin` / `password123`)
   - Start Flask server on `http://localhost:5000`

#### Frontend Setup

1. **Navigate to Frontend Directory**
   ```bash
   cd frontend
   ```

2. **Install Node Dependencies**
   ```bash
   npm install
   ```

3. **Run Frontend Development Server**
   ```bash
   npm run dev
   ```

   The frontend will start on `http://localhost:5173` (or another port if 5173 is busy)

4. **Build for Production** (optional)
   ```bash
   npm run build
   ```

#### Access the Application

- **Frontend**: Open your browser to `http://localhost:5173`
- **Backend API**: Available at `http://localhost:5000`
- Register a new account or use the admin credentials (`admin` / `password123`)

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