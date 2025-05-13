"""
LangChain Decision Agent Routes

This module defines all routes for the LangChain Decision Agent experiment.
"""

from typing import Dict, Any, Tuple, List, Optional

from flask import Blueprint, Response, jsonify, render_template, request

from src.langchain_agent.api import process_with_langchain
from src.langchain_agent.persistence.api import (
    create_persistent_agent,
    get_decision_chain,
    get_recent_chains,
)

# Create a Blueprint for LangChain routes with a URL prefix
langchain_bp = Blueprint(
    "langchain", __name__, url_prefix="/experiments/langchain-decision-agent"
)


@langchain_bp.route("/", methods=["GET"])
def index() -> str:
    """Serve the LangChain Decision Agent experiment page."""
    return render_template("experiments/langchain/index.html")


@langchain_bp.route("/api/process", methods=["POST"])
def process_text() -> Tuple[Response, int]:
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

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@langchain_bp.route("/api/chains", methods=["GET"])
def get_chains() -> Tuple[Response, int]:
    """Get recent decision chains for LangChain experiment."""
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

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@langchain_bp.route("/api/chains/<chain_id>", methods=["GET"])
def get_chain(chain_id: str) -> Tuple[Response, int]:
    """Get a specific decision chain by ID for LangChain experiment."""
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

        return jsonify(response), 200

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
