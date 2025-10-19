# Social Media Platform

A full-stack real-time social media platform built with Flask and Svelte, featuring posts, messaging, friendships, and live notifications.

![Application Demo](demos/posting.gif)

## ✨ Features

### 📱 Posts & Media
- **Create Image Posts** - Share moments with image uploads (up to 10MB)
- **Like & Unlike** - Express appreciation for posts with real-time like counters
- **Comments & Replies** - Engage with nested comment threads
- **Delete Posts** - Full control over your content

![Posts, Comments, and Likes Demo](demos/post_comm_like.gif)

*Creating posts, liking, and commenting with real-time updates*

### 💬 Real-time Messaging
- **One-on-One Chat** - Private conversations with friends
- **Image Sharing** - Send photos in messages
- **Read Receipts** - See when messages are read
- **Unread Counter** - Track new messages at a glance
- **Online Status** - See who's currently active

![Real-time Messaging Demo](demos/chatting.gif)

*Real-time messaging with instant delivery and read receipts*

### 👥 Social Features
- **Friend Requests** - Send, accept, or reject friend requests
- **Friend Management** - View your friends list and remove friends
- **User Search** - Find users by username

![Friend Requests Demo](demos/adding_friend.gif)

*Sending and managing friend requests with live notifications*

### 👤 User Profiles
- **Customizable Profiles** - Display name, bio, and avatar
- **Profile Pages** - View any user's profile with their posts
- **Avatar Upload** - Personalize your account with profile pictures
- **Password Management** - Secure password changes
- **Account Deletion** - Full control over your data

![Profile Settings Demo](demos/settings.gif)

*Customizing profile settings, uploading avatars, and managing account*

### 🔐 Authentication
- **Secure Sign Up/Sign In** - Password-hashed authentication
- **Session Management** - Persistent login sessions
- **Protected Routes** - Secure API endpoints

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd social-media-platform
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   # Create .env file
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///instance/social_media.db
   ```

5. **Initialize the database**
   ```bash
   python main.py
   ```
   The application will automatically:
   - Create the database
   - Run migrations
   - Create an admin user (username: `admin`, password: `admin`)

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Run the development server**
   ```bash
   npm run dev
   ```

### Running the Application

1. **Start the Flask backend** (from project root)
   ```bash
   python main.py
   ```
   Backend will run on `http://localhost:5000`

2. **Start the Svelte frontend** (from frontend directory)
   ```bash
   cd frontend
   npm run dev
   ```
   Frontend will run on `http://localhost:5173`

3. **Open your browser** and navigate to `http://localhost:5173`

4. **Login with default admin account**
   - Username: `admin`
   - Password: `admin`

## 🛠️ Tech Stack

### Frontend
- **Svelte 5** - Reactive component framework
- **SvelteKit 2** - Full-stack framework with routing
- **Tailwind CSS 4** - Utility-first styling
- **Socket.IO Client** - Real-time WebSocket communication
- **TypeScript** - Type safety

### Backend
- **Flask 3.0** - Python web framework
- **SQLAlchemy** - ORM for database operations
- **Flask-SocketIO** - WebSocket support
- **Werkzeug** - Password hashing and security
- **Pillow** - Image processing
- **SQLite** - Database (easily replaceable with PostgreSQL/MySQL)

## 📦 Database Schema

### User
Stores user account information and profile data.
- `id` - Primary key
- `username` - Unique username
- `password_hash` - Hashed password
- `display_name` - Display name shown on profile
- `bio` - User biography
- `avatar_path` - Path to avatar image
- `is_online` - Online status
- `last_seen` - Timestamp of last activity
- `created_at` - Account creation timestamp

### Post
Represents user posts with images.
- `id` - Primary key
- `owner` - Foreign key to User
- `image_path` - Path to post image
- `created_at`, `updated_at` - Timestamps
- **Relationships**: likes (PostLike), comments (PostComment)

### PostLike
Tracks likes on posts.
- `id` - Primary key
- `user_id` - Foreign key to User
- `post_id` - Foreign key to Post
- `created_at` - Timestamp

### PostComment
Stores comments and nested replies.
- `id` - Primary key
- `user_id` - Foreign key to User
- `post_id` - Foreign key to Post
- `parent_id` - Foreign key to parent comment (for nested replies)
- `content` - Comment text
- `created_at` - Timestamp

### Friendship
Manages friend relationships.
- `id` - Primary key
- `requester_id` - User who sent request
- `requested_id` - User who received request
- `status` - pending/accepted/rejected
- `created_at` - Timestamp

### Messenger
Contains chat conversations between two users.
- `id` - Primary key
- `first_user_id`, `second_user_id` - Foreign keys to User
- **Relationships**: messages (Message)

### Message
Individual chat messages.
- `id` - Primary key
- `sender_id`, `receiver_id` - Foreign keys to User
- `messenger_id` - Foreign key to Messenger
- `content` - Message text
- `image_url` - Path to image (optional)
- `is_read` - Read status
- `created_at` - Timestamp

### Notification
User notifications for various events.
- `id` - Primary key
- `user_id` - Foreign key to User
- `type` - Notification type (friend_request, friend_request_accepted, etc.)
- `message` - Notification message
- `data` - JSON data for the notification
- `is_read` - Read status
- `created_at` - Timestamp

## 🔌 API Documentation

### Authentication

#### Sign In
```http
POST /api/signin
Content-Type: application/json

{
  "username": "string",
  "password": "string"
}
```

#### Sign Up
```http
POST /api/signup
Content-Type: application/json

{
  "username": "string",
  "password": "string",
  "display_name": "string"
}
```

#### Get Current User
```http
GET /api/current_user
```

#### Logout
```http
GET /logout
```

### Posts

#### Get Posts Feed
```http
GET /api/posts
```
Returns all posts ordered by most recent.

#### Get User Profile
```http
GET /api/profile/<username>
```
Returns user info and their posts.

#### Create Post
```http
POST /upload_image
Content-Type: multipart/form-data

{
  "image": <file>
}
```

#### Delete Post
```http
POST /delete_post
Content-Type: application/json

{
  "post_id": <int>
}
```

#### Like/Unlike Post
```http
POST /api/like_post/<post_id>
```
Toggles like status for the post.

### Comments

#### Get Post Comments
```http
GET /api/comments/<post_id>
```

#### Create Comment
```http
POST /api/comment/<post_id>
Content-Type: application/json

{
  "content": "string",
  "parent_id": <int> // Optional, for nested replies
}
```

#### Delete Comment
```http
DELETE /api/comment/<comment_id>
```

#### Get Comment Count
```http
GET /api/comment_count/<post_id>
```

### Friends

#### Search Users
```http
GET /search_users?q=<query>
```

#### Send Friend Request
```http
POST /send_friend_request
Content-Type: application/json

{
  "username": "string"
}
```

#### Respond to Friend Request
```http
POST /respond_friend_request
Content-Type: application/json

{
  "request_id": <int>,
  "action": "accept" | "reject"
}
```

#### Cancel Friend Request
```http
POST /cancel_friend_request
Content-Type: application/json

{
  "request_id": <int>
}
```

#### Remove Friend
```http
POST /remove_friend
Content-Type: application/json

{
  "friend_id": <int>
}
```

#### Get Friends List
```http
GET /api/friends
```

#### Get Friend Requests
```http
GET /api/friend_requests
```

#### Get Sent Requests
```http
GET /api/sent_requests
```

### Messaging

#### Get Friend List with Last Messages
```http
GET /api/friend_list
```
Returns friends with last message preview and unread count.

#### Get Message History
```http
GET /api/messages/<friend_id>
```

#### Send Message
```http
POST /api/send_message
Content-Type: application/json

{
  "receiver_id": <int>,
  "content": "string"
}
```

#### Upload Chat Image
```http
POST /api/upload_chat_image
Content-Type: multipart/form-data

{
  "image": <file>,
  "receiver_id": <int>
}
```

### User Settings

#### Get User Settings
```http
GET /api/user/settings
```

#### Update Profile
```http
POST /api/user/profile
Content-Type: application/json

{
  "display_name": "string",
  "bio": "string"
}
```

#### Change Password
```http
POST /api/user/password
Content-Type: application/json

{
  "current_password": "string",
  "new_password": "string"
}
```

#### Upload Avatar
```http
POST /api/user/avatar
Content-Type: multipart/form-data

{
  "avatar": <file>
}
```

#### Delete Account
```http
DELETE /api/user/account
Content-Type: application/json

{
  "password": "string"
}
```

### Notifications

Endpoints for managing user notifications (view, read status, etc.)

## 🌐 Real-time Features (WebSocket)

The application uses Socket.IO for real-time communication. Here are the key events:

### Client → Server Events
- `connect` - User connects and joins personal room

### Server → Client Events
- `new_post` - Broadcast when a new post is created
- `post_deleted` - Notify when a post is deleted
- `post_liked` - Real-time like notification
- `post_unliked` - Real-time unlike notification
- `post_commented` - New comment notification
- `post_comment_deleted` - Comment deletion notification
- `new_message` - Incoming chat message
- `messages_read` - Message read status update
- `user_status_changed` - User online/offline status change
- `friend_list_updated` - Friend list changes
- `friend_request_rejected` - Friend request rejection
- `friend_request_cancelled` - Friend request cancellation

## 📁 Project Structure

```
social-media-platform/
├── app/                              # Flask backend
│   ├── __init__.py                   # Flask app factory
│   ├── config.py                     # Configuration management
│   ├── decorators.py                 # Custom decorators (@login_required)
│   ├── error_handlers.py             # Global error handling
│   ├── models/                       # SQLAlchemy database models
│   │   ├── user.py                   # User model
│   │   ├── post.py                   # Post, PostLike, PostComment models
│   │   ├── friendship.py             # Friendship model
│   │   ├── messenger.py              # Messenger, Message models
│   │   └── notification.py           # Notification model
│   ├── routes/                       # API route blueprints
│   │   ├── auth.py                   # Authentication routes
│   │   ├── posts.py                  # Post CRUD routes
│   │   ├── comments.py               # Comment routes
│   │   ├── friends.py                # Friendship routes
│   │   ├── chat.py                   # Messaging routes
│   │   ├── user_settings.py          # User settings routes
│   │   └── notifications.py          # Notification routes
│   ├── services/                     # Business logic layer
│   │   ├── user_service.py           # User operations
│   │   ├── post_service.py           # Post operations
│   │   ├── friendship_service.py     # Friendship logic
│   │   ├── user_settings_service.py  # Settings management
│   │   └── notification_service.py   # Notification handling
│   ├── sockets/                      # Socket.IO event handlers
│   │   └── events.py                 # WebSocket events
│   ├── helpers/                      # Helper functions
│   │   ├── chat.py                   # Chat utilities
│   │   ├── friends.py                # Friend helpers
│   │   └── notifications.py          # Notification helpers
│   └── static/                       # Static files
│       └── uploads/                  # User-uploaded files
│           ├── chat/                 # Chat images
│           └── *.jpg/png             # Post images & avatars
├── frontend/                         # Svelte SvelteKit frontend
│   ├── src/
│   │   ├── routes/                   # SvelteKit pages
│   │   │   ├── +page.svelte          # Main feed (/)
│   │   │   ├── signin/               # Login page
│   │   │   ├── signup/               # Registration page
│   │   │   ├── profile/[username]/   # User profile
│   │   │   ├── messenger/            # Chat interface
│   │   │   └── settings/             # User settings
│   │   ├── lib/
│   │   │   └── components/           # Reusable components
│   │   │       ├── Sidebar.svelte
│   │   │       ├── Post.svelte
│   │   │       ├── CreatePostWindow.svelte
│   │   │       ├── FriendsWindow.svelte
│   │   │       ├── ChatWindow.svelte
│   │   │       ├── NotificationsWindow.svelte
│   │   │       └── MessengerFriendsList.svelte
│   │   ├── app.html                  # HTML template
│   │   └── app.css                   # Global styles (Tailwind)
│   ├── package.json                  # Frontend dependencies
│   ├── svelte.config.js              # SvelteKit configuration
│   ├── vite.config.js                # Vite bundler config
│   └── tailwind.config.js            # Tailwind CSS config
├── migrations/                       # Alembic database migrations
├── instance/                         # Instance-specific files
│   └── social_media.db               # SQLite database
├── main.py                           # Application entry point
├── requirements.txt                  # Python dependencies
├── migrate_*.py                      # Database migration scripts
└── README.md                         # This file
```

## 🚢 Deployment Guide

### Preparing for Production

1. **Set environment variables**
   ```bash
   export SECRET_KEY="your-production-secret-key"
   export DATABASE_URL="postgresql://user:pass@host/db"  # Optional: Use PostgreSQL
   export FLASK_ENV="production"
   ```

2. **Build the frontend**
   ```bash
   cd frontend
   npm run build
   ```

3. **Update CORS settings** in `app/config.py`
   ```python
   # Add your production domain
   CORS_ALLOWED_ORIGINS = ['https://your-domain.com']
   ```

### Deployment Options

#### Option 1: Traditional Server (VPS)

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install gunicorn  # Production WSGI server
   ```

2. **Run with Gunicorn**
   ```bash
   gunicorn --worker-class eventlet -w 1 --bind 0.0.0.0:5000 main:app
   ```

3. **Set up Nginx as reverse proxy**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
       }
   }
   ```

#### Option 2: Heroku

1. **Create `Procfile`**
   ```
   web: gunicorn --worker-class eventlet -w 1 main:app
   ```

2. **Deploy to Heroku**
   ```bash
   heroku create your-app-name
   heroku addons:create heroku-postgresql:hobby-dev
   git push heroku main
   ```

3. **Set config vars**
   ```bash
   heroku config:set SECRET_KEY="your-secret-key"
   ```

#### Option 3: Docker

1. **Create `Dockerfile`**
   ```dockerfile
   FROM python:3.11-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   EXPOSE 5000
   CMD ["gunicorn", "--worker-class", "eventlet", "-w", "1", "--bind", "0.0.0.0:5000", "main:app"]
   ```

2. **Build and run**
   ```bash
   docker build -t social-media-platform .
   docker run -p 5000:5000 social-media-platform
   ```

### Database Migration

To switch from SQLite to PostgreSQL:

1. **Install psycopg2**
   ```bash
   pip install psycopg2-binary
   ```

2. **Update DATABASE_URL**
   ```bash
   export DATABASE_URL="postgresql://username:password@host:port/database"
   ```

3. **Run migrations**
   ```bash
   python main.py  # Will automatically create tables
   ```

### Security Considerations

- ✅ Use strong `SECRET_KEY` in production
- ✅ Enable HTTPS with SSL certificates (Let's Encrypt)
- ✅ Set secure cookie flags (`secure=True, httponly=True, samesite='Strict'`)
- ✅ Use environment variables for sensitive data
- ✅ Implement rate limiting (Flask-Limiter)
- ✅ Add CSRF protection (Flask-WTF)
- ✅ Sanitize user inputs
- ✅ Use PostgreSQL in production instead of SQLite

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

---

**Built with ❤️ using Flask and Svelte**
