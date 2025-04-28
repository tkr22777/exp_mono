"""
Web Routes

This module defines routes for web pages and UI.
"""
from flask import Blueprint, render_template

# Create a blueprint for web routes
web_bp = Blueprint('web', __name__, url_prefix='', 
                  template_folder='templates',
                  static_folder='static')

@web_bp.route("/", methods=["GET"])
def index():
    """Serve the main HTML page."""
    return render_template("index.html")

@web_bp.route("/health", methods=["GET"])
def health():
    """Health check page."""
    return "OK" 