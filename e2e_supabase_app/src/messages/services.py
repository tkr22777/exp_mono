"""
Message Services

This module contains business logic for message operations.
"""
from datetime import datetime
from ..db.supabase_client import get_supabase_client
from ..config import settings

def create_message(text, user):
    """
    Create a new message.
    
    Args:
        text: The message text
        user: The user creating the message
        
    Returns:
        dict: The created message
        
    Raises:
        Exception: If message creation fails
    """
    # Create message object
    message = {
        'text': text,
        'user_id': user.id,
        'author': user.email,  # We can store display name here if we add it to user profiles
        'created_at': datetime.now().isoformat()
    }
    
    try:
        # Insert into Supabase
        supabase = get_supabase_client()
        result = supabase.table(settings.MESSAGES_TABLE).insert(message).execute()
        
        # Get the inserted message with ID
        inserted_message = result.data[0] if result.data else None
        
        if not inserted_message:
            raise Exception('Failed to insert message')
        
        return inserted_message
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        raise Exception(f"Failed to create message: {e}")

def get_all_messages():
    """
    Get all messages.
    
    Returns:
        list: List of message objects
        
    Raises:
        Exception: If retrieval fails
    """
    try:
        # Query messages from Supabase
        supabase = get_supabase_client()
        result = supabase.table(settings.MESSAGES_TABLE) \
            .select('*') \
            .order('created_at', desc=True) \
            .execute()
        
        return result.data
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        raise Exception(f"Failed to retrieve messages: {e}")

def get_message_by_id(message_id):
    """
    Get a specific message by ID.
    
    Args:
        message_id: The ID of the message to retrieve
        
    Returns:
        dict: The message object, or None if not found
        
    Raises:
        Exception: If retrieval fails
    """
    try:
        # Query specific message from Supabase
        supabase = get_supabase_client()
        result = supabase.table(settings.MESSAGES_TABLE) \
            .select('*') \
            .eq('id', message_id) \
            .execute()
        
        return result.data[0] if result.data else None
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        raise Exception(f"Failed to retrieve message: {e}")

def delete_message(message_id, user_id):
    """
    Delete a message by ID.
    
    Args:
        message_id: The ID of the message to delete
        user_id: The ID of the user attempting to delete
        
    Returns:
        bool: True if deleted successfully
        
    Raises:
        Exception: If the message doesn't exist or user doesn't have permission
    """
    try:
        supabase = get_supabase_client()
        
        # Check if message exists and belongs to the user
        result = supabase.table(settings.MESSAGES_TABLE) \
            .select('user_id') \
            .eq('id', message_id) \
            .execute()
        
        message = result.data[0] if result.data else None
        
        if not message:
            raise Exception('Message not found')
        
        # Check message ownership
        if message['user_id'] != user_id:
            raise Exception('You do not have permission to delete this message')
        
        # Delete the message
        supabase.table(settings.MESSAGES_TABLE) \
            .delete() \
            .eq('id', message_id) \
            .execute()
        
        return True
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        # Re-raise other exceptions
        raise 