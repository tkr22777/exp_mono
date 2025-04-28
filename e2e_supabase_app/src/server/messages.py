"""
Messages Module

This module handles message-related operations using Supabase as the database.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
from .supabase_client import get_supabase_client
from .auth import login_required, get_current_user

# Create a blueprint for messages routes
messages_bp = Blueprint('messages', __name__, url_prefix='/api')

# Table name in Supabase
MESSAGES_TABLE = "messages"


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
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    # Extract message text
    text = data['text']
    
    try:
        # Create message object
        message = {
            'text': text,
            'user_id': user.id,
            'author': user.email,  # We can store display name here if we add it to user profiles
            'created_at': datetime.now().isoformat()
        }
        
        # Insert into Supabase
        supabase = get_supabase_client()
        result = supabase.table(MESSAGES_TABLE).insert(message).execute()
        
        # Get the inserted message with ID
        inserted_message = result.data[0] if result.data else None
        
        if not inserted_message:
            return jsonify({'error': 'Failed to insert message'}), 500
        
        return jsonify({'success': True, 'message': inserted_message})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages', methods=['GET'])
def get_messages():
    """
    Get all messages.
    """
    try:
        # Query messages from Supabase
        supabase = get_supabase_client()
        result = supabase.table(MESSAGES_TABLE) \
            .select('*') \
            .order('created_at', desc=True) \
            .execute()
        
        messages = result.data
        
        return jsonify({'success': True, 'messages': messages})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@messages_bp.route('/messages/<int:message_id>', methods=['GET'])
def get_message(message_id):
    """
    Get a specific message by ID.
    """
    try:
        # Query specific message from Supabase
        supabase = get_supabase_client()
        result = supabase.table(MESSAGES_TABLE) \
            .select('*') \
            .eq('id', message_id) \
            .execute()
        
        message = result.data[0] if result.data else None
        
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
    user = get_current_user()
    if not user:
        return jsonify({'error': 'User not authenticated'}), 401
    
    try:
        supabase = get_supabase_client()
        
        # Check if message exists and belongs to the user
        result = supabase.table(MESSAGES_TABLE) \
            .select('user_id') \
            .eq('id', message_id) \
            .execute()
        
        message = result.data[0] if result.data else None
        
        if not message:
            return jsonify({'success': False, 'error': 'Message not found'}), 404
        
        # Check message ownership
        if message['user_id'] != user.id:
            return jsonify({'error': 'You do not have permission to delete this message'}), 403
        
        # Delete the message
        supabase.table(MESSAGES_TABLE) \
            .delete() \
            .eq('id', message_id) \
            .execute()
        
        return jsonify({'success': True, 'message': 'Message deleted successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500 