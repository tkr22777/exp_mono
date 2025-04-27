"""
Flask Application

This module defines the Flask application for serving HTML and APIs.
"""
import os
from typing import Dict, Any, Optional, Tuple

from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS

from src.langchain_agent.api import process_with_langchain
from src.langchain_agent.persistence.api import (
    create_persistent_agent,
    get_recent_chains,
    get_decision_chain,
    save_decision_chain,
)


# Initialize Flask app
app = Flask(
    __name__, 
    static_folder="static",
    template_folder="templates"
)

# Enable CORS for all routes
CORS(app)


@app.route("/", methods=["GET"])
def index():
    """Serve the main HTML page."""
    return render_template("index.html")


@app.route("/api/process", methods=["POST"])
def process_text():
    """Process text using the LangChain agent."""
    data = request.json
    
    if not data or "text" not in data:
        return jsonify({"error": "Text is required"}), 400
    
    # Extract parameters
    text = data["text"]
    persist = data.get("persist", False)
    
    try:
        if persist:
            # Use persistent agent
            agent = create_persistent_agent()
            chain, chain_id = agent.process_text_with_persistence(text)
            
            # Convert to response format
            response = {
                "success": True,
                "result": {
                    "chain_id": chain_id,
                    "title": chain.title,
                    "final_decision": chain.final_decision,
                    "step_count": len(chain.steps),
                    "steps": [
                        {
                            "step_number": step.step_number,
                            "reasoning": step.reasoning,
                            "decision": step.decision,
                            "next_actions": step.next_actions,
                        }
                        for step in chain.steps
                    ],
                },
            }
        else:
            # Use standard agent
            chain, result = process_with_langchain(text)
            
            # Convert to response format
            response = {
                "success": True,
                "result": {
                    "chain_id": result.chain_id,
                    "title": result.title,
                    "final_decision": result.final_decision,
                    "step_count": result.step_count,
                    "steps": [
                        {
                            "step_number": step.step_number,
                            "reasoning": step.reasoning,
                            "decision": step.decision,
                            "next_actions": step.next_actions,
                        }
                        for step in chain.steps
                    ],
                },
            }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chains", methods=["GET"])
def get_chains():
    """Get recent decision chains."""
    try:
        # Get limit parameter or default to 10
        limit = request.args.get("limit", default=10, type=int)
        
        # Get chains
        chains = get_recent_chains(limit=limit)
        
        # Convert to response format
        response = {
            "success": True,
            "chains": [
                {
                    "chain_id": chain.chain_id,
                    "title": chain.title,
                    "status": chain.status,
                    "step_count": len(chain.steps),
                    "final_decision": chain.final_decision,
                }
                for chain in chains
            ],
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chains/<chain_id>", methods=["GET"])
def get_chain(chain_id):
    """Get a specific decision chain by ID."""
    try:
        # Get chain
        chain = get_decision_chain(chain_id)
        
        if not chain:
            return jsonify({"success": False, "error": "Chain not found"}), 404
        
        # Convert to response format
        response = {
            "success": True,
            "chain": {
                "chain_id": chain.chain_id,
                "title": chain.title,
                "context": chain.context,
                "status": chain.status,
                "final_decision": chain.final_decision,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "step_number": step.step_number,
                        "reasoning": step.reasoning,
                        "decision": step.decision,
                        "next_actions": step.next_actions,
                    }
                    for step in chain.steps
                ],
            },
        }
        
        return jsonify(response)
    
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        Configured Flask application
    """
    return app


def run_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    """
    Run the Flask server.
    
    Args:
        host: Host to bind the server to
        port: Port to bind the server to
        debug: Whether to run in debug mode
    """
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    # Run the server directly if this file is executed
    run_server(debug=True) 