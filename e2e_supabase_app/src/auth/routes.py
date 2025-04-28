"""
Authentication Routes

This module defines the API routes for authentication operations.
"""
from flask import Blueprint, request, jsonify, session
from ..utils.decorators import login_required
from . import services

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    """
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email']
    password = data['password']
    
    try:
        # Register user with service layer
        user, token = services.register_user(email, password)
        
        # Store token in session
        session['access_token'] = token
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user': {
                'id': user.id,
                'email': user.email
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Log in a user.
    
    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    """
    data = request.json
    
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    email = data['email']
    password = data['password']
    
    try:
        # Login user with service layer
        user, token = services.login_user(email, password)
        
        # Store token in session
        session['access_token'] = token
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': {
                'id': user.id,
                'email': user.email
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 401


@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    Log out the current user.
    """
    try:
        # Log out user from service layer
        services.logout_user()
        
        # Clear session
        session.pop('access_token', None)
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@auth_bp.route('/profile', methods=['GET'])
@login_required
def get_profile():
    """
    Get the profile of the logged-in user.
    """
    token = session.get('access_token')
    user = services.get_current_user(token)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    return jsonify({
        'success': True,
        'user': {
            'id': user.id,
            'email': user.email,
            'created_at': user.created_at
        }
    }) 