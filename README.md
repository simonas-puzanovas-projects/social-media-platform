# Social Media Platform

A Flask-based social media platform with real-time features and friend management system.

## Project Overview

This is a web-based social media platform built with Flask that allows users to register, login, manage friendships, and receive real-time notifications. The application uses WebSocket connections for live updates and features a clean, responsive user interface.

## Current Features

### Authentication System
- User registration and login
- Password hashing for security
- Session management
- Logout functionality

### User Management
- User profiles with online status tracking
- Last seen timestamps
- Admin user creation on first run

### Friend System
- Send friend requests to other users
- Accept/reject incoming friend requests
- Cancel sent friend requests
- Remove existing friends
- Real-time status updates for friends

### Search & Discovery
- User search functionality
- Live search results with friendship status indicators
- Prevent duplicate friend requests

### Notifications
- Real-time notification system using WebSocket
- Friend request notifications
- Friend request acceptance notifications
- Notification cleanup for stale requests
- Visual notification indicators in UI

### Real-time Features
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
├── main.py                 # Main Flask application
├── requirements.txt        # Python dependencies
├── templates/             # Jinja2 HTML templates
│   ├── base.html          # Base template with navigation
│   ├── login.html         # Login/registration page
│   ├── dashboard.html     # Main user dashboard
│   └── friends.html       # Friends management page
├── static/               # Static assets
│   ├── style.css         # Main stylesheet
│   └── dashboard.js      # Frontend JavaScript
└── instance/             # Database storage directory
```

## Current Routes

### Authentication
- `/` - Home redirect
- `/login` - Login page (GET/POST)
- `/register` - User registration (POST)
- `/logout` - User logout

### Main Application
- `/dashboard` - User dashboard
- `/friends` - Friends management page

### API Endpoints
- `/search_users` - User search API
- `/send_friend_request` - Send friend request
- `/respond_friend_request` - Accept/reject requests
- `/cancel_friend_request` - Cancel sent request
- `/remove_friend` - Remove existing friend
- `/api/friends` - Get friends data (JSON)
- `/api/friend_requests` - Get received requests (JSON)
- `/api/sent_requests` - Get sent requests (JSON)
- `/notifications` - Get user notifications
- `/cleanup_notifications` - Clean stale notifications

## Setup & Installation

1. Create virtual environment: `python -m venv venv`
2. Activate virtual environment: `venv\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r requirements.txt`
4. Run application: `python main.py`
5. Access at: `http://localhost:5000`

## Default Admin Account
- Username: `admin`
- Password: `password123`

## TODO: Next Feature - Chat System

The next major feature to implement is a real-time chat system that will allow friends to communicate with each other. This will include:

- Direct messaging between friends
- Real-time message delivery using WebSocket
- Message history and persistence
- Online status indicators
- Typing indicators
- Message read receipts

The chat system will integrate with the existing friendship system to ensure only friends can message each other, and will use the established WebSocket infrastructure for real-time communication.