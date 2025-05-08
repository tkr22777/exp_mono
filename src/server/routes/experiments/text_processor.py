"""
Text Processor Routes

This module defines all routes for the Text Processor experiment.
"""

from flask import Blueprint, jsonify, render_template, request
from flask_socketio import emit

# Import the SocketIO instance and text processor
from src.server.socketio_instance import socketio
from src.text_processor.processor import process_text

# Create a Blueprint for Text Processor routes with a URL prefix
text_processor_bp = Blueprint(
    "text_processor", __name__, url_prefix="/experiments/text-processor"
)

# Experiment configuration parameters
EXPERIMENT_CONFIG = {
    "debounce_delay_ms": 100,
    "default_text": "",
    "max_text_length": 5000,
}


@text_processor_bp.route("/", methods=["GET"])
def index():
    """Serve the Text Processor experiment page."""
    return render_template(
        "experiments/text_processor/index.html", config=EXPERIMENT_CONFIG
    )


@text_processor_bp.route("/api/process", methods=["POST"])
def handle_process_text():
    """Process text for the Text Processor experiment."""
    data = request.json

    if not data or "text" not in data:
        return jsonify({"error": "Text is required"}), 400

    try:
        # Process text returns string directly now
        response_text = process_text(data["text"])
        
        # Simple response with a single field
        return jsonify({
            "success": True, 
            "result": {
                "response": response_text
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print("Client connected to Socket.IO")
    emit('message', {'data': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print("Client disconnected from Socket.IO")


@socketio.on('join')
def on_join(data):
    """Handle client joining a namespace."""
    namespace = data.get('namespace', '')
    print(f"Client joining namespace: {namespace}")
    emit('message', {'data': f'Joined {namespace}'})


@socketio.on('process_text')
def handle_process_text(data):
    """Process text via Socket.IO and stream results."""
    if not data or "text" not in data:
        emit('error', {"message": "Text is required"})
        return

    text = data["text"]
    session_id = request.sid
    print(f"Processing text for session: {session_id}")

    try:
        emit('processing_start', {"status": "started"})
        
        # Process text with session tracking - returns string directly now
        response_text = process_text(text, session_id)
        
        # Send the complete response in one chunk instead of line by line
        emit('processing_update', {"chunk": response_text})
        
        # Signal processing complete
        emit('processing_complete', {"status": "complete"})

    except Exception as e:
        print(f"Error processing text: {str(e)}")
        emit('error', {"message": str(e)})


@socketio.on('process_audio')
def handle_process_audio(data):
    """Process audio via Socket.IO and stream results."""
    if not data or "audio_data" not in data:
        emit('error', {"message": "Audio data is required"})
        return

    try:
        emit('processing_start', {"status": "started"})
        
        # Demo transcription (would be replaced with actual API call)
        demo_text = "42"  # Use a number for our calculator
        
        # Process text with session tracking - returns string directly now
        response_text = process_text(demo_text, request.sid)
        
        # Send the complete response in one chunk
        emit('processing_update', {"chunk": response_text})
        
        # Signal processing complete
        emit('processing_complete', {"status": "complete"})

    except Exception as e:
        emit('error', {"message": f"Error processing audio: {str(e)}"})
