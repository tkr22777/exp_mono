"""
Web Routes

This module defines routes for web pages and UI.
"""

from flask import Blueprint, redirect, render_template, session, url_for

# Create a blueprint for web routes
web_bp = Blueprint(
    "web",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder="static",
    static_url_path="/static/web",
)  # Distinct static URL path


@web_bp.route("/", methods=["GET"])
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@web_bp.route("/login", methods=["GET"])
def login():
    """Serve the login page."""
    # If user is already logged in, redirect to profile
    if "access_token" in session:
        return redirect(url_for("web.profile"))
    return render_template("login.html")


@web_bp.route("/profile", methods=["GET"])
def profile():
    """Serve the user profile page."""
    # If user is not logged in, redirect to login
    if "access_token" not in session:
        return redirect(url_for("web.login"))
    return render_template("profile.html")


@web_bp.route("/health", methods=["GET"])
def health():
    """Health check page."""
    return "OK"
