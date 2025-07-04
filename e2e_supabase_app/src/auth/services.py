"""
Authentication Services

This module contains business logic for authentication operations.
"""
import logging
from datetime import datetime

import jwt

from ..config import settings
from ..db.supabase_client import get_supabase_client


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
            token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        # Extract user ID from payload
        user_id = payload.get("sub")
        if not user_id:
            logging.error("Token missing 'sub' claim containing user ID")
            return None

        # Check if we have a stored Supabase token
        supabase_token = payload.get("supabase_token")

        if supabase_token:
            try:
                supabase = get_supabase_client()
                response = supabase.auth.get_user(supabase_token)
                return response.user
            except Exception as auth_error:
                logging.warning(f"Stored Supabase token is invalid: {auth_error}")

        # Fallback to JWT payload data
        return {
            "id": user_id,
            "email": payload.get("email"),
            "created_at": datetime.utcfromtimestamp(payload.get("iat", 0)).isoformat()
            if payload.get("iat")
            else datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logging.error(f"Error decoding token: {e}")
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
        response = supabase.auth.sign_up({"email": email, "password": password})

        user = response.user
        session = response.session

        # Get the Supabase token if available
        supabase_token = None
        if session:
            supabase_token = session.access_token

        # Create JWT token
        token = create_auth_token(user, supabase_token)

        return user, token
    except ValueError as e:
        logging.error(f"Supabase connection error during registration: {e}")
        raise Exception(f"Registration service unavailable. Please try again later.")
    except Exception as e:
        logging.error(f"Registration failed: {e}")
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
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        user = response.user
        session = response.session

        # Get the Supabase token if available
        supabase_token = None
        if session:
            supabase_token = session.access_token

        # Create JWT token
        token = create_auth_token(user, supabase_token)

        return user, token
    except ValueError as e:
        logging.error(f"Supabase connection error during login: {e}")
        raise Exception(f"Login service unavailable. Please try again later.")
    except Exception as e:
        logging.error(f"Login failed: {e}")
        raise Exception(f"Invalid email or password. Please try again.")


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
        logging.error(f"Supabase connection error during logout: {e}")
        raise Exception(f"Logout service unavailable. Please try again later.")
    except Exception as e:
        logging.error(f"Logout failed: {e}")
        raise Exception(f"Logout failed: {e}")


def create_auth_token(user, supabase_token=None):
    """
    Create a JWT token for a user.

    Args:
        user: The user object to create a token for
        supabase_token: Optional Supabase session token to include

    Returns:
        str: The JWT token
    """
    payload = {
        "sub": user.id,
        "email": user.email,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + settings.JWT_EXPIRATION_DELTA,
    }

    # Store Supabase token in the payload if available
    if supabase_token:
        payload["supabase_token"] = supabase_token

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return token
