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

    # Extract the text
    text = data["text"]

    try:
        # Simple mock processing function (capitalize the text)
        processed_text = text.upper()

        # Return the processed text
        response = {"success": True, "result": {"processed_text": processed_text}}

        return jsonify(response)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# WebSocket routes
@socketio.on("connect", namespace="/experiments/text-processor/ws")
def ws_connect():
    """Handle WebSocket connection."""
    print("Client connected to text processor WebSocket")


@socketio.on("disconnect", namespace="/experiments/text-processor/ws")
def ws_disconnect():
    """Handle WebSocket disconnection."""
    print("Client disconnected from text processor WebSocket")


@socketio.on("process_text", namespace="/experiments/text-processor/ws")
def ws_process_text(data):
    """Process text via WebSocket and stream results."""
    if not data or "text" not in data:
        emit("error", {"message": "Text is required"})
        return

    text = data["text"]

    try:
        # Notify client that processing has started
        emit("processing_start", {"status": "started"})

        # Simulate streaming processing - in a real implementation,
        # this would call an actual streaming API
        words = text.split()
        for i, word in enumerate(words):
            # Process each word (simulated by converting to uppercase)
            processed_chunk = word.upper() + " "
            
            # Emit the processed chunk
            emit("processing_update", {"chunk": processed_chunk})
            
            # Simulate processing delay
            if i < len(words) - 1:
                # Sleep between words (in a real implementation, this would be handled by the streaming API)
                socketio.sleep(0.1)

        # Notify client that processing is complete
        emit("processing_complete", {"status": "complete"})

    except Exception as e:
        emit("error", {"message": str(e)})


@socketio.on("process_audio", namespace="/experiments/text-processor/ws")
def ws_process_audio(data):
    """Process audio via WebSocket and stream transcription/analysis results."""
    if not data or "audio_data" not in data:
        emit("error", {"message": "Audio data is required"})
        return

    try:
        # Notify client that processing has started
        emit("processing_start", {"status": "started"})

        # In a real implementation, this would send the audio to a
        # streaming transcription service
        
        # For demo, simulate streaming transcription results
        demo_transcription = "THIS IS A SIMULATED TRANSCRIPTION OF AUDIO. "
        demo_transcription += "THE ACTUAL IMPLEMENTATION WOULD USE A REAL SPEECH-TO-TEXT API. "
        demo_transcription += "IMAGINE THE TEXT APPEARING WORD BY WORD AS THE AUDIO IS PROCESSED."
        
        words = demo_transcription.split()
        for i, word in enumerate(words):
            # Emit each word as it's "transcribed"
            emit("processing_update", {"chunk": word + " "})
            
            # Add delay between words to simulate real-time transcription
            socketio.sleep(0.2)
        
        # Notify client that processing is complete
        emit("processing_complete", {"status": "complete"})

    except Exception as e:
        emit("error", {"message": f"Error processing audio: {str(e)}"})
