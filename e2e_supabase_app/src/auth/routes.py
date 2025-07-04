"""
Authentication Routes

This module defines the API routes for authentication operations.
"""
import logging

from flask import Blueprint, jsonify, request, session

from ..utils.decorators import login_required
from . import services

# Create a blueprint for authentication routes
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


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
        # Register user with service layer
        user, token = services.register_user(email, password)

        # Store token in session
        session["access_token"] = token

        # Get user data
        if isinstance(user, dict):
            user_data = {"id": user.get("id"), "email": user.get("email")}
        else:
            user_data = {"id": user.id, "email": user.email}

        return jsonify(
            {
                "success": True,
                "message": "User registered successfully",
                "user": user_data,
            }
        )
    except Exception as e:
        logging.error(f"Registration failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400


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
        # Login user with service layer
        user, token = services.login_user(email, password)

        # Store token in session
        session["access_token"] = token
        session.modified = True  # Ensure the session is saved

        # Get user data
        if isinstance(user, dict):
            user_data = {"id": user.get("id"), "email": user.get("email")}
        else:
            user_data = {"id": user.id, "email": user.email}

        return jsonify(
            {"success": True, "message": "Login successful", "user": user_data}
        )
    except Exception as e:
        logging.error(f"Login failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 401


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """
    Log out the current user.
    """
    try:
        # Log out user from service layer
        services.logout_user()

        # Clear session
        session.pop("access_token", None)
        session.modified = True  # Ensure the session is saved

        return jsonify({"success": True, "message": "Logged out successfully"})
    except Exception as e:
        logging.error(f"Logout failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 400


@auth_bp.route("/profile", methods=["GET"])
@login_required
def get_profile():
    """
    Get the profile of the logged-in user.
    """
    try:
        token = session.get("access_token")
        user = services.get_current_user(token)

        if not user:
            logging.error("User not found for valid token")
            return jsonify({"success": False, "error": "User not found"}), 404

        # Get user data based on type
        if isinstance(user, dict):
            user_data = {
                "id": user.get("id"),
                "email": user.get("email"),
                "created_at": user.get("created_at"),
            }
        else:
            user_data = {
                "id": user.id,
                "email": user.email,
                "created_at": user.created_at,
            }

        return jsonify({"success": True, "user": user_data})
    except Exception as e:
        logging.error(f"Error fetching profile: {str(e)}")
        return (
            jsonify({"success": False, "error": f"Error fetching profile: {str(e)}"}),
            500,
        )
