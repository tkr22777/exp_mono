"""
Main Routes

This module defines the main routes for the application's landing page.
"""

from flask import Blueprint, render_template

# Create a Blueprint for main routes
main_bp = Blueprint("main", __name__)


@main_bp.route("/", methods=["GET"])
def index() -> str:
    """Serve the main HTML page."""
    return render_template("index.html")
