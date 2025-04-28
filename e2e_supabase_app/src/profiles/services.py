"""
Profile Services

This module contains business logic for user profile operations.
"""
from ..db.supabase_client import get_supabase_client, get_admin_client

# Table name in Supabase
PROFILES_TABLE = "user_profiles"

def get_profile_by_id(user_id):
    """
    Get a user profile by user ID.
    
    Args:
        user_id: The ID of the user to get the profile for
        
    Returns:
        dict: The user profile, or None if not found
    """
    try:
        supabase = get_supabase_client()
        response = supabase.table(PROFILES_TABLE) \
            .select('*') \
            .eq('id', user_id) \
            .execute()
        
        profiles = response.data
        return profiles[0] if profiles else None
    except Exception as e:
        raise Exception(f"Failed to get profile: {str(e)}")

def get_all_profiles():
    """
    Get all user profiles (admin function).
    
    Returns:
        list: List of all user profiles
    """
    try:
        # Use admin client for this operation
        supabase = get_admin_client()
        response = supabase.table(PROFILES_TABLE) \
            .select('*') \
            .execute()
        
        return response.data
    except Exception as e:
        raise Exception(f"Failed to get profiles: {str(e)}")

def create_profile(user):
    """
    Create a new user profile.
    
    Args:
        user: The user to create a profile for
        
    Returns:
        dict: The created profile
    """
    try:
        # Get display name from email (first part before @)
        email = user.email 
        display_name = email.split('@')[0] if email else "User"
        
        profile_data = {
            'id': user.id,
            'email': email,
            'display_name': display_name,
            'avatar_url': None,
            'metadata': {}
        }
        
        supabase = get_supabase_client()
        response = supabase.table(PROFILES_TABLE) \
            .insert(profile_data) \
            .execute()
        
        profiles = response.data
        return profiles[0] if profiles else None
    except Exception as e:
        raise Exception(f"Failed to create profile: {str(e)}")

def update_profile(user_id, update_data):
    """
    Update a user profile.
    
    Args:
        user_id: The ID of the user to update the profile for
        update_data: Dictionary containing the fields to update
        
    Returns:
        dict: The updated profile
    """
    try:
        # Ensure we're not updating the id
        if 'id' in update_data:
            del update_data['id']
        
        supabase = get_supabase_client()
        response = supabase.table(PROFILES_TABLE) \
            .update(update_data) \
            .eq('id', user_id) \
            .execute()
        
        profiles = response.data
        return profiles[0] if profiles else None
    except Exception as e:
        raise Exception(f"Failed to update profile: {str(e)}")

def update_profile_metadata(user_id, metadata_updates):
    """
    Update specific fields in a user's metadata.
    
    Args:
        user_id: The ID of the user to update metadata for
        metadata_updates: Dictionary containing the metadata fields to update
        
    Returns:
        dict: The updated profile
    """
    try:
        # First, get the current profile to access existing metadata
        current_profile = get_profile_by_id(user_id)
        if not current_profile:
            raise Exception(f"Profile not found for user ID: {user_id}")
        
        # Get current metadata or initialize empty dict
        current_metadata = current_profile.get('metadata', {})
        
        # Merge the updates with existing metadata
        updated_metadata = {**current_metadata, **metadata_updates}
        
        # Update the profile with new metadata
        return update_profile(user_id, {'metadata': updated_metadata})
    except Exception as e:
        raise Exception(f"Failed to update profile metadata: {str(e)}") 