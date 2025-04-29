"""
Application Settings

This module is responsible for loading and providing access to application settings.
It loads environment variables and provides unified access to configuration values.
"""
import datetime
import os

from dotenv import load_dotenv

# Load environment variables from .env file with force override
load_dotenv(override=True)

# Flask settings
FLASK_APP = os.getenv("FLASK_APP", "src.server.app:create_app()")
FLASK_ENV = os.getenv("FLASK_ENV", "development")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "1") == "1"

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Security settings
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")  # Used for session encryption
SESSION_TYPE = "filesystem"
SESSION_PERMANENT = False
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=7)

# JWT configuration
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_DELTA = datetime.timedelta(days=1)


def get_flask_config():
    """
    Get Flask application configuration dictionary.

    Returns:
        dict: Flask configuration dictionary
    """
    return {
        "SECRET_KEY": SECRET_KEY,
        "SESSION_TYPE": SESSION_TYPE,
        "SESSION_PERMANENT": SESSION_PERMANENT,
        "PERMANENT_SESSION_LIFETIME": PERMANENT_SESSION_LIFETIME,
    }
