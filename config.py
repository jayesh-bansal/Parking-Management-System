import os
import secrets

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_urlsafe(32)
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'parking_app.db'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    # Fixed key for development convenience
    SECRET_KEY = 'dev-parking-app-secret-key-2024-do-not-use-in-production'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    # Must be set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    def __init__(self):
        if not self.SECRET_KEY:
            raise ValueError("SECRET_KEY environment variable must be set in production!")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DATABASE_PATH = ':memory:'  # In-memory database for tests
    SECRET_KEY = 'testing-secret-key-not-for-production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
