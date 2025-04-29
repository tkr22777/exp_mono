"""
Authentication Decorators

This module provides decorators for authentication and authorization.
"""
import logging
from functools import wraps

import jwt
from flask import current_app, jsonify, request, session


def login_required(f):
    """
    Decorator to require login for a route.
    Checks for valid JWT in session, Authorization header, or cookies.

    Args:
        f: The function to decorate

    Returns:
        The decorated function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check for token in multiple places
        token = None

        # Check session first
        token = session.get("access_token")

        # If not in session, check Authorization header
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")

        # If still not found, check cookies
        if not token:
            token = request.cookies.get("access_token")

        # Final fallback for Supabase token in cookies
        if not token:
            token = request.cookies.get("supabase-auth-token")

        if not token:
            logging.warning(f"No authentication token found for {request.path}")
            return jsonify({"success": False, "error": "Authentication required"}), 401

        try:
            # Verify token
            decoded = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )

        except jwt.ExpiredSignatureError:
            logging.warning("JWT token expired")
            return (
                jsonify(
                    {"success": False, "error": "Token expired, please login again"}
                ),
                401,
            )
        except jwt.InvalidTokenError as e:
            logging.error(f"Invalid JWT token: {str(e)}")
            return (
                jsonify({"success": False, "error": "Invalid authentication token"}),
                401,
            )
        except Exception as e:
            logging.error(f"Unexpected error while validating token: {str(e)}")
            return jsonify({"success": False, "error": "Authentication error"}), 401

        return f(*args, **kwargs)

    return decorated_function
