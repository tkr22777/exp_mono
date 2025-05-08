"""
Text Processor Routes

This module defines all routes for the Text Processor experiment.
"""

from flask import Blueprint, jsonify, render_template, request
from flask_socketio import emit

# Import the SocketIO instance (will be initialized in app.py)
from src.server.socketio_instance import socketio

# Create a Blueprint for Text Processor routes with a URL prefix
text_processor_bp = Blueprint(
    "text_processor", __name__, url_prefix="/experiments/text-processor"
)

# Experiment configuration parameters
EXPERIMENT_CONFIG = {
    "debounce_delay_ms": 1,  # Debounce delay in milliseconds
    "default_text": "",  # Default text to show in the input area
    "max_text_length": 5000,  # Maximum allowed text length
}


def process_text_with_alternating_case(text):
    """
    Process text with alternating case (uppercase/lowercase words).
    
    Args:
        text: The input text to process
        
    Returns:
        A list of processed chunks (words with alternating case)
    """
    words = text.split()
    return [word.upper() if i % 2 == 0 else word.lower() for i, word in enumerate(words)]


@text_processor_bp.route("/", methods=["GET"])
def index():
    """Serve the Text Processor experiment page."""
    return render_template(
        "experiments/text_processor/index.html", config=EXPERIMENT_CONFIG
    )


@text_processor_bp.route("/api/process", methods=["POST"])
def process_text():
    """Process text for the Text Processor experiment."""
    data = request.json

    if not data or "text" not in data:
        return jsonify({"error": "Text is required"}), 400

    try:
        processed_chunks = process_text_with_alternating_case(data["text"])
        processed_text = " ".join(processed_chunks)
        return jsonify({"success": True, "result": {"processed_text": processed_text}})

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
        
        processed_chunks = process_text_with_alternating_case(text)
        
        for chunk in processed_chunks:
            emit('processing_update', {"chunk": chunk + " ", "session_id": session_id})
            # Minimal delay to prevent UI freezing while still appearing real-time
            socketio.sleep(0.01)  

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
        demo_text = "THIS IS A SIMULATED TRANSCRIPTION OF AUDIO. THE ACTUAL IMPLEMENTATION WOULD USE A REAL SPEECH-TO-TEXT API."
        processed_chunks = process_text_with_alternating_case(demo_text)
        
        for chunk in processed_chunks:
            emit('processing_update', {"chunk": chunk + " "})
            # Minimal delay for realistic transcription appearance
            socketio.sleep(0.05)
        
        emit('processing_complete', {"status": "complete"})

    except Exception as e:
        emit('error', {"message": f"Error processing audio: {str(e)}"})
