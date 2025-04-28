"""
Supabase Client Module

This module provides the Supabase client configuration for interacting with
Supabase services (authentication, database, storage, etc.).
"""
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Get Supabase configuration from environment
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Supabase URL and API key must be set in the .env file"
    )

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create admin client with service role key for privileged operations
# Use this client only for operations that require special privileges
# and cannot be performed with the anonymous key
if SUPABASE_SERVICE_KEY:
    admin_supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
else:
    admin_supabase = None
    
def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    
    Returns:
        Supabase client configured with the project URL and API key
    """
    return supabase

def get_admin_client() -> Client:
    """
    Get the Supabase admin client instance with service role permissions.
    
    Returns:
        Supabase client with service role key, or None if not configured
    """
    if not admin_supabase:
        raise ValueError("Service role key not configured in environment variables")
    return admin_supabase 