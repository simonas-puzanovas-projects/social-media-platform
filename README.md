# Social Media Platform

A Flask-based social media platform with real-time features and friend management system.

## Project Overview

This is a web-based social media platform built with Flask that allows users to register, login, manage friendships, and receive real-time notifications. The application uses WebSocket connections for live updates and features a clean, responsive user interface.

## Current Features

### ✅ Authentication System
- User registration and login
- Password hashing for security
- Session management
- Logout functionality

### ✅ User Management
- User profiles with online status tracking
- Last seen timestamps
- Basic profile display

### ✅ Friend System
- Send friend requests to other users
- Accept/reject incoming friend requests
- Cancel sent friend requests
- Remove existing friends
- Real-time status updates for friends
- Complete API endpoints for friend data

### ✅ Search & Discovery
- User search functionality
- Live search results with friendship status indicators
- Prevent duplicate friend requests

### ✅ Notifications
- Real-time notification system using WebSocket
- Friend request notifications
- Friend request acceptance notifications
- Notification cleanup for stale requests
- Visual notification indicators in UI
- Toast notification system

### ✅ Real-time Features
- WebSocket integration with Flask-SocketIO
- Live online/offline status updates
- Real-time notifications
- Auto-cleanup of invalid notifications

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **Real-time**: Flask-SocketIO for WebSocket connections
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Werkzeug password hashing
- **Styling**: Custom CSS with responsive design

## Database Models

### User
- ID, username, password hash
- Online status and last seen tracking
- Relationships to friendships and notifications

### Friendship
- Bidirectional friendship model
- Status tracking (pending, accepted)
- Requester and requested user references

### Notification
- User-specific notifications
- Type-based categorization
- JSON data storage for additional information
- Read/unread status tracking

## File Structure

```
social-media-platform/
├── main.py                       # Application entry point
├── requirements.txt              # Python dependencies
├── app/                          # Main application package
│   ├── __init__.py              # App factory and configuration
│   ├── models/                  # Database models
│   │   └── __init__.py          # User, Friendship, Notification models
│   ├── routes/                  # Route blueprints
│   │   ├── __init__.py          # Blueprint imports
│   │   ├── auth.py              # Authentication routes
│   │   ├── index.py             # Home page route
│   │   ├── friends.py           # Friends management routes
│   │   └── notifications.py     # Notification routes
│   ├── socket/                  # WebSocket handlers
│   │   └── __init__.py          # Socket.IO event handlers
│   ├── templates/               # Jinja2 HTML templates
│   │   ├── index.html           # Base template with navigation
│   │   ├── home.html            # User home page
│   │   ├── login.html           # Login/registration page
│   │   ├── friends.html         # Friends management page
│   │   └── toast_notification.html # Toast notification component
│   └── static/                  # Static assets
│       ├── style.css            # Main stylesheet
│       ├── index.js             # Base JavaScript with Socket.IO
│       ├── home.js              # Home page functionality
│       ├── friends.js           # Friends page functionality
│       └── toast_notification.js # Toast notification system
└── instance/                    # Database storage directory
```

## Current Routes

### Authentication (`bp_auth`)
- `/login` - Login page (GET/POST)
- `/register` - User registration (POST)
- `/logout` - User logout

### Main Application (`bp_index`)
- `/` - Home page (redirects to login if not authenticated)

### Friends Management (`bp_friends`)
- `/friends` - Friends management page
- `/search_users` - User search API (GET)
- `/send_friend_request` - Send friend request (POST)
- `/respond_friend_request` - Accept/reject requests (POST)
- `/cancel_friend_request` - Cancel sent request (POST)
- `/remove_friend` - Remove existing friend (POST)

### API Endpoints (`bp_friends`)
- `/api/friends` - Get friends data (JSON)
- `/api/friend_requests` - Get received requests (JSON)
- `/api/sent_requests` - Get sent requests (JSON)

### Notifications (`bp_notifications`)
- `/notifications` - Get user notifications (JSON)
- `/cleanup_notifications` - Clean stale notifications (POST)

## Setup & Installation

1. Create virtual environment: `python -m venv venv`
2. Activate virtual environment: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. **Database Setup**: Currently commented out in `main.py` - needs manual initialization
5. Run application: `python main.py`
6. Access at: `http://localhost:5000`


## TODO: Next Feature - Chat System

The next major feature to implement is a real-time chat system that will allow friends to communicate with each other. This will include:

- Direct messaging between friends
- Real-time message delivery using WebSocket
- Message history and persistence
- Online status indicators
- Typing indicators
- Message read receipts

The chat system will integrate with the existing friendship system to ensure only friends can message each other, and will use the established WebSocket infrastructure for real-time communication.