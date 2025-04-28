"""
Message Routes

This module defines the API routes for message operations.
"""
from flask import Blueprint, request, jsonify, session
from ..utils.decorators import login_required
from ..auth.services import get_current_user
from . import services

# Create a blueprint for messages routes
messages_bp = Blueprint('messages', __name__, url_prefix='/api')

@messages_bp.route('/message', methods=['POST'])
@login_required
def add_message():
    """
    Add a new message to the database.
    
    Expected JSON payload:
    {
        "text": "Message content"
    }
    """
    data = request.json
    
    if not data or 'text' not in data:
        return jsonify({'error': 'Message text is required'}), 400
    
    # Get current user
    token = session.get('access_token')
    user = get_current_user(token)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    # Extract message text
    text = data['text']
    
    try:
        # Create message using service layer
        message = services.create_message(text, user)
        return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    Get all messages.
    """
    try:
        # Get messages using service layer
        messages = services.get_all_messages()
        return jsonify({'success': True, 'messages': messages})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """
    Get a specific message by ID.
    """
    try:
        # Get message using service layer
        message = services.get_message_by_id(message_id)
        
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        return jsonify({'success': True, 'message': message})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    """
    Delete a message by ID (only if it belongs to the current user).
    """
    # Get current user
    token = session.get('access_token')
    user = get_current_user(token)
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        # Delete message using service layer
        services.delete_message(message_id, user.id)
        return jsonify({'success': True, 'message': 'Message deleted successfully'})
    
    except Exception as e:
        # Determine the appropriate error code based on the exception message
        if 'not found' in str(e).lower():
            return jsonify({'success': False, 'error': str(e)}), 404
        elif 'permission' in str(e).lower():
            return jsonify({'error': str(e)}), 403
        else:
            return jsonify({'error': str(e)}), 500 