"""
Authentication Decorators

This module provides decorators for authentication and authorization.
"""
from functools import wraps
from flask import jsonify, session, current_app, request
import jwt
import logging

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
        
        if current_app.debug:
            logging.info(f"Request path: {request.path}")
            logging.info(f"Session contains access_token: {'access_token' in session}")
            if token:
                logging.info(f"Token length: {len(token)}")
                logging.info(f"Token starts with: {token[:10]}...")
        
        if not token:
            logging.warning(f"No access_token in session for {request.path}")
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        try:
            # Verify token
            decoded = jwt.decode(
                token, 
                current_app.config['SECRET_KEY'], 
                algorithms=["HS256"]
            )
            
            if current_app.debug:
                logging.info(f"Successfully decoded token with user_id: {decoded.get('sub')}")
                
        except jwt.ExpiredSignatureError:
            logging.warning("JWT token expired")
            return jsonify({
                'success': False,
                'error': 'Token expired, please login again'
            }), 401
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid JWT token: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Invalid authentication token'
            }), 401
        except Exception as e:
            logging.error(f"Unexpected error while validating token: {str(e)}")
            return jsonify({
                'success': False,
                'error': 'Authentication error'
            }), 401
            
        return f(*args, **kwargs)
    return decorated_function 