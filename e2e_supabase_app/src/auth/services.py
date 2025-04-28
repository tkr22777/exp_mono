"""
Authentication Services

This module contains business logic for authentication operations.
"""
import jwt
from datetime import datetime
from ..db.supabase_client import get_supabase_client
from ..config import settings

def get_current_user(token):
    """
    Get the current logged-in user from a session token.
    
    Args:
        token: The JWT token from the session
        
    Returns:
        User data if token is valid, None otherwise
    """
    if not token:
        return None
    
    try:
        # Decode token to get user info
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        # Retrieve user from Supabase
        try:
            supabase = get_supabase_client()
            response = supabase.auth.get_user(token)
            return response.user
        except ValueError as e:
            # Handle Supabase connection errors
            print(f"Error retrieving user from Supabase: {e}")
            return None
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def register_user(email, password):
    """
    Register a new user with Supabase.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        tuple: (user object, JWT token)
        
    Raises:
        Exception: If registration fails
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        user = response.user
        
        # Create JWT token
        token = create_auth_token(user)
        
        return user, token
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        raise Exception(f"Registration failed: {e}")

def login_user(email, password):
    """
    Log in a user with email and password.
    
    Args:
        email: User's email address
        password: User's password
        
    Returns:
        tuple: (user object, JWT token)
        
    Raises:
        Exception: If login fails
    """
    try:
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        user = response.user
        
        # Create JWT token
        token = create_auth_token(user)
        
        return user, token
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        raise Exception(f"Login failed: {e}")

def logout_user():
    """
    Log out the current user from Supabase.
    
    Raises:
        Exception: If logout fails
    """
    try:
        supabase = get_supabase_client()
        supabase.auth.sign_out()
    except ValueError as e:
        # Handle Supabase connection errors
        raise Exception(f"Supabase connection error: {e}")
    except Exception as e:
        raise Exception(f"Logout failed: {e}")

def create_auth_token(user):
    """
    Create a JWT token for a user.
    
    Args:
        user: The user object to create a token for
        
    Returns:
        str: The JWT token
    """
    payload = {
        'sub': user.id,
        'email': user.email,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + settings.JWT_EXPIRATION_DELTA
    }
    
    return jwt.encode(
        payload, 
        settings.SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    ) 