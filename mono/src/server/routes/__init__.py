"""
Routes Package

This package contains all route definitions for the application,
organized into separate modules by feature/experiment.
"""

from .experiments import langchain_bp, mcp_server_bp, text_processor_bp
from .main_routes import main_bp

__all__ = ["main_bp", "langchain_bp", "mcp_server_bp", "text_processor_bp"]
