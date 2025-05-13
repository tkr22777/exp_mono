"""
Text Processor Routes

This module defines all routes for the Text Processor experiment.
"""

from typing import Dict, Any, Tuple, Union, cast

from flask import Blueprint, Response, jsonify, render_template, request
from flask_socketio import emit, request as socketio_request
from pydantic import ValidationError

# Import the SocketIO instance and text processor
from src.server.socketio_instance import socketio
from src.modules.text_processor.processor import process_text
from src.modules.text_processor.models.api import TextProcessRequest, TextProcessResponse
from src.modules.text_processor.models.domain import ProcessingResult

# Create a Blueprint for Text Processor routes with a URL prefix
text_processor_bp = Blueprint(
    "text_processor", __name__, url_prefix="/experiments/text-processor"
)

# Experiment configuration parameters
EXPERIMENT_CONFIG: Dict[str, Any] = {
    "debounce_delay_ms": 100,
    "default_text": "",
    "max_text_length": 5000,
}


@text_processor_bp.route("/", methods=["GET"])
def index() -> str:
    """Serve the Text Processor experiment page."""
    return render_template(
        "experiments/text_processor/index.html", config=EXPERIMENT_CONFIG
    )


@text_processor_bp.route("/api/process", methods=["POST"])
def handle_process_text() -> Tuple[Response, int]:
    """Process text for the Text Processor experiment."""
    data = request.json

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        # Convert to request model
        req = TextProcessRequest(**data)
        
        # Process text
        response_text = process_text(req.text, req.session_id)
        
        # Create result and response
        result = ProcessingResult(response=response_text, session_id=req.session_id)
        response = TextProcessResponse.from_result(result)
        
        # Return response
        return jsonify(response.dict()), 200
    except ValidationError as e:
        return jsonify(TextProcessResponse.from_error(str(e)).dict()), 400
    except Exception as e:
        return jsonify(TextProcessResponse.from_error(str(e)).dict()), 500


# Socket.IO event handlers
@socketio.on("connect")
def handle_connect() -> None:
    """Handle client connection."""
    print("Client connected to Socket.IO")
    emit("message", {"data": "Connected to server"})


@socketio.on("disconnect")
def handle_disconnect() -> None:
    """Handle client disconnection."""
    print("Client disconnected from Socket.IO")


@socketio.on("join")
def on_join(data: Dict[str, Any]) -> None:
    """Handle client joining a namespace."""
    namespace = data.get("namespace", "")
    print(f"Client joining namespace: {namespace}")
    emit("message", {"data": f"Joined {namespace}"})


@socketio.on("process_text")
def handle_process_text_socket(data: Dict[str, Any]) -> None:
    """Process text via Socket.IO and stream results."""
    if not data or "text" not in data:
        emit("error", {"message": "Text is required"})
        return

    text = data["text"]
    session_id = socketio_request.sid
    print(f"Processing text for session: {session_id}")

    try:
        emit("processing_start", {"status": "started"})

        # Process text with session tracking
        response_text = process_text(text, session_id)

        # Send the complete response in one chunk instead of line by line
        emit("processing_update", {"chunk": response_text})

        # Signal processing complete
        emit("processing_complete", {"status": "complete"})

    except Exception as e:
        print(f"Error processing text: {str(e)}")
        emit("error", {"message": str(e)})


@socketio.on("process_audio")
def handle_process_audio(data: Dict[str, Any]) -> None:
    """Process audio via Socket.IO and stream results."""
    if not data or "audio_data" not in data:
        emit("error", {"message": "Audio data is required"})
        return

    try:
        emit("processing_start", {"status": "started"})

        # Demo transcription (would be replaced with actual API call)
        demo_text = "42"  # Use a number for our calculator

        # Process text with session tracking
        response_text = process_text(demo_text, socketio_request.sid)

        # Send the complete response in one chunk
        emit("processing_update", {"chunk": response_text})

        # Signal processing complete
        emit("processing_complete", {"status": "complete"})

    except Exception as e:
        emit("error", {"message": f"Error processing audio: {str(e)}"})
