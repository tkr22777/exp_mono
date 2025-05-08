"""
Text Processor Module

This module contains functionality for text processing using an LLM with minimal context.
The implementation demonstrates a simple conversational workflow where:
1. Only the last response from the LLM is stored in the session state
2. This last response is included in the next prompt to provide minimal context
3. The system message guides the LLM to perform as a calculator for demo purposes
"""
import json
from typing import Dict, List, Optional, Tuple
from src.llms import default_client

# Session state to track conversation history
# Structure: {session_id: {"last_response": "assistant response", "history": [messages]}}
SESSION_STATE: Dict[str, Dict[str, any]] = {}

def get_session_state(session_id: str) -> Dict[str, any]:
    """
    Get state for a session, initializing if needed
    
    Args:
        session_id: Unique session identifier
        
    Returns:
        Session state dictionary
    """
    if session_id not in SESSION_STATE:
        SESSION_STATE[session_id] = {"last_response": "", "history": []}
    return SESSION_STATE[session_id]

def is_valid_number(text: str) -> bool:
    """
    Check if the input text is a valid number
    
    Args:
        text: Input text to validate
        
    Returns:
        True if the input text is a valid number, False otherwise
    """
    text = text.strip()
    try:
        float(text)
        return True
    except (ValueError, TypeError):
        return False

def generate_llm_response(prompt: str, session_id: Optional[str] = None) -> str:
    """
    Generate a response using an LLM based on the prompt and conversation history.
    This demonstrates a minimal context approach where we track just enough history
    for the LLM to perform calculations properly.
    
    Args:
        prompt: The user's input text
        session_id: The session identifier for accessing the conversation history
        
    Returns:
        Generated response text
    """
    # First validate if the input is a number to ensure the LLM is only used for numbers
    if not is_valid_number(prompt):
        return "Please provide a valid number."
    
    try:
        # Create system message with explicit instructions for the calculator behavior
        system_content = (
            "You are a calculator assistant that adds numbers. Follow these rules exactly:\n"
            "1. If this is the first number in the conversation, respond with exactly: 'You entered: NUMBER'\n"
            "2. For subsequent numbers, add the new number to the previous result and respond with: 'PREVIOUS_RESULT + NEW_NUMBER = NEW_RESULT'\n"
            "3. Always perform addition correctly and maintain the running total\n"
            "4. Do not include any extra explanations or text in your response\n"
            "5. Pay close attention to the conversation history to determine the current total\n"
            "6. If I give you number 1, then 2, then 3, your responses should be: 'You entered: 1', '1 + 2 = 3', '3 + 3 = 6'"
        )
        system_message = {"role": "system", "content": system_content}
        
        # Get the session state
        state = get_session_state(session_id) if session_id else {"last_response": "", "history": []}
        
        # Build conversation history
        messages = [system_message]
        
        # Add conversation history if we have a session
        if session_id:
            # If we have previous history, include it
            history = state.get("history", [])
            if history:
                messages.extend(history)
            
        # Add the current user message
        user_message = {"role": "user", "content": prompt}
        messages.append(user_message)
        
        # Log the messages being sent to the LLM for debugging
        print(f"[LLM Request] Session: {session_id}, Messages: {json.dumps(messages, indent=2)}")
        
        # Call generate_response through the default_client
        response = default_client.generate_response(messages=messages)
        print(f"[LLM Response] Session: {session_id}, Response: {response}")
        
        # If we have a session ID, update the conversation history
        if session_id and response:
            # Add the user message and assistant response to history
            if not state["history"]:
                # If this is the first interaction, make sure to include the system message too
                state["history"] = [system_message]
                
            state["history"].append(user_message)
            assistant_message = {"role": "assistant", "content": response.strip()}
            state["history"].append(assistant_message)
            
            # Limit history to the last 4 messages (2 exchanges) to keep context minimal
            if len(state["history"]) > 5:  # system message + 2 exchanges
                state["history"] = [state["history"][0]] + state["history"][-4:]
                
            # Also update last_response for backward compatibility
            state["last_response"] = response.strip()
            
            # Log the updated session state
            print(f"[Session State] Session: {session_id}, History length: {len(state['history'])}")
        
        return response.strip() if response else "No response generated"
        
    except Exception as e:
        print(f"Error generating LLM response: {str(e)}")
        return f"I encountered an issue: {str(e)}"

def process_text(text: str, session_id: Optional[str] = None) -> str:
    """
    Process text using an LLM with minimal context
    
    Args:
        text: The input text to process
        session_id: Session identifier for tracking the conversation history
        
    Returns:
        The generated response text
    """
    if not text:
        return "Please enter a number."
    
    print(f"[process_text] Processing: '{text}' for session: {session_id}")
    
    # Generate LLM response with context if session_id is provided
    response = generate_llm_response(text, session_id)
    
    print(f"[process_text] Response: '{response}' for session: {session_id}")
    return response
    