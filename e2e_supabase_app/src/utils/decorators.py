"""
Authentication Decorators

This module provides decorators for authentication and authorization.
"""
from functools import wraps
from flask import jsonify, session, current_app
import jwt

def login_required(f):
    """
    Decorator to require login for a route.
    Checks for valid JWT in session.
    
    Args:
        f: The function to decorate
        
    Returns:
        The decorated function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        token = session.get('access_token')
        if not token:
            return jsonify({'error': 'Authentication required'}), 401
        
        try:
            # Verify token
            jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=["HS256"]
            )
        except:
            return jsonify({'error': 'Invalid or expired token'}), 401
            
        return f(*args, **kwargs)
    return decorated_function 