"""
Profile Routes

This module defines API routes for user profile operations.
"""
from flask import Blueprint, request, jsonify, session
from ..utils.decorators import login_required
from ..auth.services import get_current_user
from . import services

# Create a blueprint for profiles routes
profiles_bp = Blueprint('profiles', __name__, url_prefix='/api/profiles')

@profiles_bp.route("/me", methods=["GET"])
@login_required
def get_my_profile():
    """Get the current user's profile."""
    # Check for token in multiple places
    token = session.get('access_token')
    
    # If not in session, check Authorization header
    if not token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    # If still not found, check cookies
    if not token:
        token = request.cookies.get('access_token')
    
    # Final fallback for Supabase token in cookies
    if not token:
        token = request.cookies.get('supabase-auth-token')
    
    user = get_current_user(token)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        profile = services.get_profile_by_id(user.id)
        
        if not profile:
            # Create a profile if it doesn't exist
            profile = services.create_profile(user)
            
        return jsonify({
            'success': True,
            'profile': profile
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route("/me", methods=["PATCH"])
@login_required
def update_my_profile():
    """Update the current user's profile."""
    # Check for token in multiple places
    token = session.get('access_token')
    
    # If not in session, check Authorization header
    if not token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    # If still not found, check cookies
    if not token:
        token = request.cookies.get('access_token')
    
    # Final fallback for Supabase token in cookies
    if not token:
        token = request.cookies.get('supabase-auth-token')
    
    user = get_current_user(token)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No update data provided'}), 400
        
        profile = services.update_profile(user.id, data)
        
        return jsonify({
            'success': True,
            'profile': profile
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route("/me/metadata", methods=["PATCH"])
@login_required
def update_my_metadata():
    """Update specific fields in the current user's metadata."""
    # Check for token in multiple places
    token = session.get('access_token')
    
    # If not in session, check Authorization header
    if not token:
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
    
    # If still not found, check cookies
    if not token:
        token = request.cookies.get('access_token')
    
    # Final fallback for Supabase token in cookies
    if not token:
        token = request.cookies.get('supabase-auth-token')
    
    user = get_current_user(token)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        data = request.json
        if not data:
            return jsonify({'error': 'No metadata updates provided'}), 400
        
        profile = services.update_profile_metadata(user.id, data)
        
        return jsonify({
            'success': True,
            'profile': profile
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@profiles_bp.route("/<user_id>", methods=["GET"])
def get_profile(user_id):
    """Get a user's profile by ID."""
    try:
        profile = services.get_profile_by_id(user_id)
        
        if not profile:
            return jsonify({
                'success': False,
                'error': 'Profile not found'
            }), 404
            
        return jsonify({
            'success': True,
            'profile': profile
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500 