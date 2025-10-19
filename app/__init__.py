from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
import os
from flask_cors import CORS


db = SQLAlchemy()
socketio = SocketIO()

def app_init():

    app = Flask(__name__)

    # Load configuration
    config_name = os.environ.get('FLASK_ENV', 'development')
    from .config import config
    app.config.from_object(config[config_name])

    db.init_app(app)

    from .services import init_services
    init_services(db)

 # Use configured CORS origins instead of wildcard
    cors_origins = app.config.get('CORS_ALLOWED_ORIGINS', ['http://localhost:5000'])
    print(f"Config name: {config_name}")
    print(f"CORS origins: {cors_origins}")

    CORS(app, supports_credentials=True, origins=cors_origins)

    # For development, disable CORS entirely if needed
    if config_name == 'development':
        socketio.init_app(app, cors_allowed_origins="*")
    else:
        socketio.init_app(app, cors_allowed_origins=cors_origins)   

    from .routes import bp_auth
    from .routes import bp_index
    from .routes import bp_friends
    from .routes import bp_notifications
    from .routes import bp_chat
    from .routes import bp_settings

    app.register_blueprint(bp_index)
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_friends)
    app.register_blueprint(bp_notifications)
    app.register_blueprint(bp_chat)
    app.register_blueprint(bp_settings)

    # Register error handlers and logging
    from .error_handlers import register_error_handlers, setup_logging
    register_error_handlers(app)
    setup_logging(app)

    from . import sockets

    return app
    

