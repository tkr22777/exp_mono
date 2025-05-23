"""
Text Processor Service

Implements calculator functionality using LLMs with conversation history.
"""

import json
import logging
from typing import List, Optional, Dict, Any, cast

from src.modules.text_processor.repositories.interfaces import SessionRepository
from src.modules.llms.ai_client import AIClient, Message
from src.modules.llms import AIClientError
from src.modules.text_processor.models.domain import ProcessingResult, SessionState, Message as DomainMessage

# Configure logger for this module
logger = logging.getLogger(__name__)


class TextProcessorService:
    """Calculator service that maintains running totals across conversation turns."""
    
    def __init__(self, session_repository: SessionRepository, ai_client: AIClient):
        """Initialize with required dependencies."""
        self.session_repository = session_repository
        self.ai_client = ai_client
    
    def is_valid_number(self, text: str) -> bool:
        """Validate if input can be parsed as a float."""
        text = text.strip()
        try:
            float(text)
            return True
        except (ValueError, TypeError):
            return False
    
    def process_text(self, text: str, session_id: Optional[str] = None) -> ProcessingResult:
        """
        Process numerical input and maintain running total across conversation turns.
        
        Args:
            text: Numerical input to process
            session_id: Optional session identifier for conversation continuity
            
        Returns:
            Processing result with calculated response
        """
        if not text:
            return ProcessingResult(response="Please enter a number.", session_id=session_id)
        
        logger.info(f"Processing text: '{text}' for session: {session_id}")
        response = self._generate_llm_response(text, session_id)
        logger.info(f"Generated response: '{response}' for session: {session_id}")
        
        return ProcessingResult(response=response, session_id=session_id)
    
    def _generate_llm_response(self, prompt: str, session_id: Optional[str] = None) -> str:
        """
        Generate calculator response using conversation history.
        
        Implementation note: First number shows as "You entered: X", 
        subsequent inputs add to running total "X + Y = Z".
        """
        # First validate if the input is a number
        if not self.is_valid_number(prompt):
            return "Please provide a valid number."
        
        try:
            # Create system message for calculator behavior
            system_content = (
                "You are a calculator assistant that adds numbers. Follow these rules exactly:\n"
                "1. If this is the first number in the conversation, respond with exactly: 'You entered: NUMBER'\n"
                "2. For subsequent numbers, add the new number to the previous result and respond with: 'PREVIOUS_RESULT + NEW_NUMBER = NEW_RESULT'\n"
                "3. Always perform addition correctly and maintain the running total\n"
                "4. Do not include any extra explanations or text in your response\n"
                "5. Pay close attention to the conversation history to determine the current total\n"
                "6. If I give you number 1, then 2, then 3, your responses should be: 'You entered: 1', '1 + 2 = 3', '3 + 3 = 6'"
            )
            system_message: Message = {"role": "system", "content": system_content}
            
            # Build messages list
            messages: List[Message] = [system_message]
            
            # Get session state if session_id is provided
            if session_id:
                state = self.session_repository.get_session(session_id)
                
                # Add conversation history if we have it
                if state.history:
                    for msg in state.history:
                        messages.append({"role": msg.role, "content": msg.content})
            
            # Add the current user message
            user_message: Message = {"role": "user", "content": prompt}
            messages.append(user_message)
            
            logger.debug(f"Sending request to LLM for session {session_id}: {json.dumps(messages, indent=2)}")
            response = self.ai_client.generate_response(messages=messages)
            logger.debug(f"Received response from LLM for session {session_id}: {response}")
            
            # Update session state if we have a session ID
            if session_id and response:
                state = self.session_repository.get_session(session_id)
                
                # Create a new history list if needed
                if not state.history:
                    state.history = [DomainMessage(role="system", content=system_content)]
                
                # Add the user message and assistant response to history
                state.history.append(DomainMessage(role="user", content=prompt))
                state.history.append(DomainMessage(role="assistant", content=response.strip()))
                
                # Limit history to system message + 2 exchanges
                if len(state.history) > 5:
                    state.history = [state.history[0]] + state.history[-4:]
                
                # Update last_response for backward compatibility
                state.last_response = response.strip()
                self.session_repository.save_session(session_id, state)
                logger.debug(f"Updated session state for session {session_id}, history length: {len(state.history)}")
            
            return response.strip() if response else "No response generated"
            
        except AIClientError as e:
            logger.error(f"AI client error while generating response: {str(e)}", exc_info=True)
            return f"I encountered an AI processing issue: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error generating LLM response: {str(e)}", exc_info=True)
            return f"I encountered an unexpected issue: {str(e)}" 