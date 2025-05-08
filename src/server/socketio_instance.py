"""
SocketIO Instance

This module creates and exports a Flask-SocketIO instance that can be shared across the application.
"""

from flask_socketio import SocketIO

# Create the SocketIO instance
# cors_allowed_origins="*" allows connections from any origin
# async_mode="gevent" is recommended for production
socketio = SocketIO(cors_allowed_origins="*", async_mode=None)

def init_socketio(app):
    """
    Initialize SocketIO with the Flask app.
    
    Args:
        app: The Flask application instance
    
    Returns:
        The initialized SocketIO instance
    """
    socketio.init_app(app)
    return socketio 