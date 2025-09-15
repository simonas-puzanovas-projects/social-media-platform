from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db = SQLAlchemy()
socketio = SocketIO()

def app_init():

    app = Flask(__name__)

    app.config['SECRET_KEY'] = 'your-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    socketio.init_app(app, cors_allowed_origins="*")
    from . import socket

    from .routes import bp_auth
    from .routes import bp_index
    from .routes import bp_friends
    from .routes import bp_notifications
    from .routes import bp_chat

    app.register_blueprint(bp_index)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_friends)
    app.register_blueprint(bp_notifications)
    app.register_blueprint(bp_chat)

    return app
    

