"""
Authentication Module for Supabase

This module handles user authentication using Supabase Auth services.
"""
from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Blueprint, current_app, jsonify, request, session
from werkzeug.security import generate_password_hash

from .supabase_client import get_supabase_client

# Create a blueprint for authentication routes
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def login_required(f):
    """
    Decorator to require login for a route.
    Checks for valid JWT in session.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if user is logged in
        token = session.get("access_token")
        if not token:
            return jsonify({"error": "Authentication required"}), 401

        try:
            # Verify token
            jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
        except:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)

    return decorated_function


def get_current_user():
    """
    Get the current logged-in user.

    Returns:
        User data if logged in, None otherwise
    """
    token = session.get("access_token")
    if not token:
        return None

    try:
        # Decode token to get user info
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
        )
        user_id = payload.get("sub")

        # Retrieve user from Supabase
        supabase = get_supabase_client()
        response = supabase.auth.get_user(token)
        return response.user
    except:
        return None


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.

    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    """
    data = request.json

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    try:
        # Register user with Supabase Auth
        supabase = get_supabase_client()
        response = supabase.auth.sign_up({"email": email, "password": password})

        user = response.user

        # Create JWT token
        payload = {
            "sub": user.id,
            "email": user.email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=1),
        }

        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

        # Store token in session
        session["access_token"] = token

        return jsonify(
            {
                "success": True,
                "message": "User registered successfully",
                "user": {"id": user.id, "email": user.email},
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in a user.

    Expected JSON payload:
    {
        "email": "user@example.com",
        "password": "secure_password"
    }
    """
    data = request.json

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password are required"}), 400

    email = data["email"]
    password = data["password"]

    try:
        # Login user with Supabase Auth
        supabase = get_supabase_client()
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        user = response.user

        # Create JWT token
        payload = {
            "sub": user.id,
            "email": user.email,
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=1),
        }

        token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

        # Store token in session
        session["access_token"] = token

        return jsonify(
            {
                "success": True,
                "message": "Login successful",
                "user": {"id": user.id, "email": user.email},
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Log out the current user.
    """
    try:
        # Log out user from Supabase
        supabase = get_supabase_client()
        supabase.auth.sign_out()

        # Clear session
        session.pop("access_token", None)

        return jsonify({"success": True, "message": "Logged out successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@auth_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """
    Get the profile of the logged-in user.
    """
    user = get_current_user()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(
        {
            "success": True,
            "user": {"id": user.id, "email": user.email, "created_at": user.created_at},
        }
    )
