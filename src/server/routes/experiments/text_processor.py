"""
Text Processor Routes

This module defines all routes for the Text Processor experiment.
"""

from flask import Blueprint, jsonify, render_template, request

# Create a Blueprint for Text Processor routes with a URL prefix
text_processor_bp = Blueprint(
    "text_processor", __name__, url_prefix="/experiments/text-processor"
)

# Experiment configuration parameters
EXPERIMENT_CONFIG = {
    "debounce_delay_ms": 5000,  # Debounce delay in milliseconds
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
