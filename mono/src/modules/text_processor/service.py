"""
Text Processor Service

Implements text transformation functionality using LLMs with conversation history.
"""

import json
import logging
from typing import Any, Dict, List, Optional

from src.modules.llms import AIClientError
from src.modules.llms.ai_client import AIClient, Message
from src.modules.text_processor.models.domain import Message as DomainMessage
from src.modules.text_processor.models.domain import ProcessingResult, SessionState
from src.modules.text_processor.repositories.interfaces import SessionRepository

# Configure logger for this module
logger = logging.getLogger(__name__)


class TextProcessorService:
    """Text transformation service that maintains and modifies text state across conversation turns."""

    def __init__(self, session_repository: SessionRepository, ai_client: AIClient):
        """Initialize with required dependencies."""
        self.session_repository = session_repository
        self.ai_client = ai_client

    def process_text(
        self, text: str, session_id: Optional[str] = None
    ) -> ProcessingResult:
        """
        Process text input and maintain text state across conversation turns.

        Args:
            text: Text input to process or modify
            session_id: Optional session identifier for conversation continuity

        Returns:
            Processing result with transformed text response
        """
        if not text.strip():
            return ProcessingResult(
                response="Please provide some text to work with.", session_id=session_id
            )

        logger.info(f"Processing text: '{text}' for session: {session_id}")
        
        # Check if we have existing text state
        current_text = self._get_current_text_state(session_id) if session_id else None
        
        if current_text:
            # Two-step process for transformations
            logger.info(f"Using two-step process for transformation. Current text: '{current_text}'")
            response = self._two_step_transformation(text, current_text, session_id)
        else:
            # Single-step process for establishing initial state
            logger.info("No existing text state, using single-step process")
            response = self._generate_llm_response(text, session_id)
        
        logger.info(f"Generated response: '{response}' for session: {session_id}")

        return ProcessingResult(response=response, session_id=session_id)

    def _get_current_text_state(self, session_id: str) -> Optional[str]:
        """Extract the current text state from session history."""
        try:
            state = self.session_repository.get_session(session_id)
            if not state.history or len(state.history) < 3:  # Need at least system + user + assistant
                return None
            
            # Find the last assistant response that contains actual text content
            for message in reversed(state.history):
                if message.role == "assistant":
                    response = message.content.strip()
                    # Skip responses that are asking for input
                    if not any(phrase in response.lower() for phrase in [
                        "provide some text", "establish", "initial state", "text to work with"
                    ]):
                        return response
            
            return None
        except Exception as e:
            logger.error(f"Error getting current text state: {str(e)}")
            return None

    def _two_step_transformation(self, user_message: str, current_text: str, session_id: Optional[str] = None) -> str:
        """
        Perform two-step transformation: first analyze intent, then execute transformation.
        
        Args:
            user_message: The user's transformation request
            current_text: The current text state to transform
            session_id: Optional session identifier
            
        Returns:
            The transformed text
        """
        try:
            # Step 1: Analyze intent
            intent_analysis = self._analyze_intent(user_message, current_text)
            logger.debug(f"Intent analysis result: {intent_analysis}")
            
            # Step 2: Execute transformation
            transformed_text = self._execute_transformation(current_text, intent_analysis, session_id)
            logger.debug(f"Transformation result: {transformed_text}")
            
            return transformed_text
            
        except Exception as e:
            logger.error(f"Error in two-step transformation: {str(e)}")
            # Fallback to single-step process
            return self._generate_llm_response(user_message, session_id)

    def _analyze_intent(self, user_message: str, current_text: str) -> str:
        """
        Analyze user intent for transformation.
        
        Args:
            user_message: The user's message
            current_text: The current text state
            
        Returns:
            Analysis of what the user wants to do
        """
        system_content = (
            "You are an expert at analyzing user intent for text transformations. "
            "Given the current text and a user's message, identify what transformation they want to perform.\n\n"
            
            "Your job is to:\n"
            "1. Understand what the user wants to change about the current text\n"
            "2. Identify the specific transformation type and parameters\n"
            "3. Provide a clear, actionable description of the intent\n\n"
            
            "TRANSFORMATION CATEGORIES:\n"
            "- COLOR_CHANGE: Change color of object (e.g., 'make it red', 'change to blue')\n"
            "- SIZE_CHANGE: Modify size (e.g., 'make it bigger', 'tiny', 'huge')\n"
            "- OBJECT_SUBSTITUTION: Replace the main object (e.g., 'make it a cat', 'change to car')\n"
            "- QUANTITY_CHANGE: Singular/plural changes (e.g., 'make it plural', 'singular')\n"
            "- ATTRIBUTE_ADD: Add new attributes (e.g., 'add wings', 'with a hat', 'old and rusty')\n"
            "- ATTRIBUTE_REMOVE: Remove attributes (e.g., 'remove the hat', 'without wings')\n"
            "- GRAMMAR_CHANGE: Tense or grammatical changes (e.g., 'past tense', 'future tense')\n"
            "- STYLE_CHANGE: Stylistic modifications (e.g., 'more formal', 'casual tone')\n"
            "- COMPLEX_MODIFICATION: Multiple changes or complex instructions\n\n"
            
            "OUTPUT FORMAT:\n"
            "Category: [TRANSFORMATION_CATEGORY]\n"
            "Intent: [Clear description of what to change]\n"
            "Specifics: [Detailed parameters for the transformation]\n\n"
            
            "EXAMPLES:\n"
            "Current text: 'a blue car'\n"
            "User: 'make it red'\n"
            "Output:\n"
            "Category: COLOR_CHANGE\n"
            "Intent: Change the color from blue to red\n"
            "Specifics: Replace 'blue' with 'red' while keeping all other attributes\n\n"
            
            "Current text: 'a small dog'\n"
            "User: 'add wings and make it purple'\n"
            "Output:\n"
            "Category: COMPLEX_MODIFICATION\n"
            "Intent: Add wings to the dog and change its color to purple\n"
            "Specifics: Add 'wings' as an attribute and change color to 'purple' while keeping size 'small'"
        )
        
        messages: List[Message] = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"Current text: '{current_text}'\nUser message: '{user_message}'\n\nAnalyze the intent:"}
        ]
        
        response = self.ai_client.generate_response(messages=messages)
        return response.strip() if response else "Unable to analyze intent"

    def _execute_transformation(self, current_text: str, intent_analysis: str, session_id: Optional[str] = None) -> str:
        """
        Execute the transformation based on intent analysis.
        
        Args:
            current_text: The text to transform
            intent_analysis: The analyzed intent from the first step
            session_id: Optional session identifier
            
        Returns:
            The transformed text
        """
        system_content = (
            "You are an expert text transformer. Your job is to modify text based on analyzed intent.\n\n"
            
            "INSTRUCTIONS:\n"
            "1. You will receive the current text and an intent analysis\n"
            "2. Apply the transformation exactly as described in the intent\n"
            "3. Preserve all attributes not mentioned in the transformation\n"
            "4. Return ONLY the final transformed text, no explanations\n"
            "5. Maintain natural language flow and readability\n\n"
            
            "TRANSFORMATION PRINCIPLES:\n"
            "- Be precise: Only change what's explicitly requested\n"
            "- Be conservative: Preserve original structure when possible\n"
            "- Be natural: Ensure the result reads fluently\n"
            "- Be consistent: Apply transformations uniformly\n\n"
            
            "EXAMPLES:\n"
            "Current text: 'a bright blue cow'\n"
            "Intent: Change color from blue to red\n"
            "Output: 'a bright red cow'\n\n"
            
            "Current text: 'the old house'\n"
            "Intent: Add wings and make it magical\n"
            "Output: 'the old magical house with wings'"
        )
        
        messages: List[Message] = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": f"Current text: '{current_text}'\n\nIntent analysis:\n{intent_analysis}\n\nExecute the transformation:"}
        ]
        
        response = self.ai_client.generate_response(messages=messages)
        transformed_text = response.strip() if response else current_text
        
        # Update session state with the transformation
        if session_id and transformed_text:
            self._update_session_with_transformation(session_id, intent_analysis, transformed_text)
        
        return transformed_text

    def _update_session_with_transformation(self, session_id: str, intent_analysis: str, transformed_text: str) -> None:
        """Update session state with transformation details."""
        try:
            state = self.session_repository.get_session(session_id)
            
            # Add the intent analysis and transformation to history
            if state.history:
                # Find the last user message
                user_message = None
                for msg in reversed(state.history):
                    if msg.role == "user":
                        user_message = msg.content
                        break
                
                if user_message:
                    # Add the final response to history
                    state.history.append(DomainMessage(role="assistant", content=transformed_text))
                    
                    # Limit history to system message + last 4 exchanges
                    if len(state.history) > 9:
                        state.history = [state.history[0]] + state.history[-8:]
                    
                    # Update last_response
                    state.last_response = transformed_text
                    self.session_repository.save_session(session_id, state)
                    logger.debug(f"Updated session with transformation result for session {session_id}")
                    
        except Exception as e:
            logger.error(f"Error updating session with transformation: {str(e)}")

    def _generate_llm_response(
        self, prompt: str, session_id: Optional[str] = None
    ) -> str:
        """
        Generate text transformation response using conversation history.
        Used for establishing initial text state.
        """
        try:
            # Create system message for text establishment
            system_content = (
                "You are an expert text transformation assistant. Your job is to establish initial text state.\n\n"
                
                "DECISION LOGIC:\n"
                "1. If the message is CONTENT (descriptive text) → Echo it back to establish state\n"
                "2. If the message is INSTRUCTION without context → Ask for content first\n\n"
                
                "CONTENT vs INSTRUCTION:\n"
                "CONTENT (can establish state): 'a blue car', 'the tall building', 'children playing'\n"
                "INSTRUCTIONS (need context): 'make it red', 'bigger', 'with double e'\n\n"
                
                "EXAMPLES:\n"
                "User: 'a bright blue cow' → You: 'a bright blue cow'\n"
                "User: 'make it purple' → You: 'Please provide some text to establish the initial state, then I can apply transformations like making it purple.'\n"
                "User: 'with double e' → You: 'Please provide some text content first, then I can modify it with your requested changes.'"
            )
            
            system_message: Message = {"role": "system", "content": system_content}
            messages: List[Message] = [system_message]

            # Get session state if session_id is provided
            if session_id:
                state = self.session_repository.get_session(session_id)
                if state.history:
                    for msg in state.history:
                        messages.append({"role": msg.role, "content": msg.content})

            # Add the current user message
            user_message: Message = {"role": "user", "content": prompt}
            messages.append(user_message)

            response = self.ai_client.generate_response(messages=messages)
            
            # Update session state
            if session_id and response:
                state = self.session_repository.get_session(session_id)
                
                if not state.history:
                    state.history = [DomainMessage(role="system", content=system_content)]
                
                state.history.append(DomainMessage(role="user", content=prompt))
                state.history.append(DomainMessage(role="assistant", content=response.strip()))
                
                # Limit history
                if len(state.history) > 9:
                    state.history = [state.history[0]] + state.history[-8:]
                
                state.last_response = response.strip()
                self.session_repository.save_session(session_id, state)

            return response.strip() if response else "No response generated"

        except AIClientError as e:
            logger.error(f"AI client error while generating response: {str(e)}", exc_info=True)
            return f"I encountered an AI processing issue: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error generating LLM response: {str(e)}", exc_info=True)
            return f"I encountered an unexpected issue: {str(e)}"
