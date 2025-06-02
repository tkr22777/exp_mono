"""
Reusable Decorators for Error Handling

This module provides decorators for consistent error handling across
Flask routes and Socket.IO handlers.
"""

import logging
from functools import wraps
from typing import Any, Callable, Dict, Tuple

from flask import Response, jsonify
from flask_socketio import emit

logger = logging.getLogger(__name__)


def handle_mcp_errors(func: Callable) -> Callable:
    """
    Decorator for standardizing MCP error handling in Flask routes.
    
    Automatically catches exceptions and returns appropriate JSON responses.
    Logs full error details for debugging.
    
    Usage:
        @handle_mcp_errors
        def my_route():
            # Route logic that might fail
            return {"success": True, "data": result}
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Tuple[Response, int]:
        try:
            result = func(*args, **kwargs)
            # If function returns a tuple (response, status_code), return as-is
            if isinstance(result, tuple):
                return result
            # If function returns just data, wrap in success response
            return jsonify({"success": True, **result}), 200
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            return jsonify({
                "success": False,
                "error": str(e),
                "message": "An error occurred while processing your request"
            }), 500
    return wrapper


def emit_on_error(success_event: str, error_event: str = "mcp_error") -> Callable:
    """
    Decorator for Socket.IO handlers that automatically emits errors.
    
    Args:
        success_event: Event to emit on successful execution
        error_event: Event to emit on error (default: "mcp_error")
    
    Usage:
        @emit_on_error("mcp_tool_result")
        def handle_tool_call(data):
            # Handler logic that might fail
            result = call_some_function(data)
            return {"tool_name": "test", "result": result}
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> None:
            try:
                result = func(*args, **kwargs)
                if result is not None:
                    emit(success_event, {"success": True, **result})
                else:
                    emit(success_event, {"success": True})
            except Exception as e:
                logger.error(f"Error in Socket.IO handler {func.__name__}: {str(e)}", exc_info=True)
                emit(error_event, {
                    "message": str(e),
                    "handler": func.__name__
                })
        return wrapper
    return decorator


def validate_json_data(required_fields: list = None) -> Callable:
    """
    Decorator to validate JSON request data.
    
    Args:
        required_fields: List of required field names
        
    Usage:
        @validate_json_data(["tool_name", "arguments"])
        def my_route():
            # request.json is guaranteed to have required fields
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from flask import request
            
            if not request.json:
                return jsonify({
                    "success": False,
                    "error": "JSON data required"
                }), 400
            
            if required_fields:
                missing_fields = [field for field in required_fields 
                                if field not in request.json]
                if missing_fields:
                    return jsonify({
                        "success": False,
                        "error": f"Missing required fields: {', '.join(missing_fields)}"
                    }), 400
            
            return func(*args, **kwargs)
        return wrapper
    return decorator 