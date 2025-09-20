import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///users.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # CORS configuration
    CORS_ALLOWED_ORIGINS = os.environ.get('CORS_ALLOWED_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')

    # Upload configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'app/static/uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 10485760))  # 10MB default

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Explicitly allow common development origins
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5000",
        "http://127.0.0.1:5000",
        "http://0.0.0.0:5000"
    ]

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Note: In production, SECRET_KEY should be set via environment variables

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}