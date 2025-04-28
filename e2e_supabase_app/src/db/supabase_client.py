"""
Supabase Client Module

This module provides the Supabase client configuration for interacting with
Supabase services (authentication, database, storage, etc.).
"""
from supabase import create_client, Client
from ..config import settings

# Global variables to hold client instances
_supabase_client = None
_admin_supabase_client = None

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance, creating it if needed.
    
    Returns:
        Supabase client configured with the project URL and API key
        
    Raises:
        ValueError: If Supabase URL or API key is missing or invalid
    """
    global _supabase_client
    
    if _supabase_client is None:
        # Validate configuration
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("Supabase URL and API key must be set in the .env file")
        
        try:
            # Create client
            _supabase_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        except Exception as e:
            raise ValueError(f"Failed to create Supabase client: {str(e)}")
    
    return _supabase_client

def get_admin_client() -> Client:
    """
    Get the Supabase admin client instance with service role permissions.
    Creates the client if it doesn't exist yet.
    
    Returns:
        Supabase client with service role key
        
    Raises:
        ValueError: If service role key is not configured or invalid
    """
    global _admin_supabase_client
    
    if _admin_supabase_client is None:
        if not settings.SUPABASE_SERVICE_KEY:
            raise ValueError("Service role key not configured in environment variables")
            
        try:
            # Create admin client
            _admin_supabase_client = create_client(
                settings.SUPABASE_URL, 
                settings.SUPABASE_SERVICE_KEY
            )
        except Exception as e:
            raise ValueError(f"Failed to create Supabase admin client: {str(e)}")
    
    return _admin_supabase_client 