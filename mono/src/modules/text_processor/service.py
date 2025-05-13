"""
Text Processor Service

This module contains the business logic for text processing.
"""

import json
from typing import List, Optional, Dict, Any, cast

from src.modules.text_processor.repositories.interfaces import SessionRepository
from src.modules.llms.ai_client import AIClient, Message
from src.modules.text_processor.models.domain import ProcessingResult, SessionState, Message as DomainMessage


class TextProcessorService:
    """Service for processing text using AI models."""
    
    def __init__(self, session_repository: SessionRepository, ai_client: AIClient):
        """
        Initialize the text processor service.
        
        Args:
            session_repository: Repository for session data
            ai_client: Client for AI model interactions
        """
        self.session_repository = session_repository
        self.ai_client = ai_client
    
    def is_valid_number(self, text: str) -> bool:
        """
        Check if the input text is a valid number.
        
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
    
    def process_text(self, text: str, session_id: Optional[str] = None) -> ProcessingResult:
        """
        Process text using an LLM with minimal context.
        
        Args:
            text: The input text to process
            session_id: Session identifier for tracking the conversation history
            
        Returns:
            Processing result
        """
        if not text:
            return ProcessingResult(response="Please enter a number.", session_id=session_id)
        
        print(f"[process_text] Processing: '{text}' for session: {session_id}")
        
        # Generate LLM response with context if session_id is provided
        response = self._generate_llm_response(text, session_id)
        
        print(f"[process_text] Response: '{response}' for session: {session_id}")
        return ProcessingResult(response=response, session_id=session_id)
    
    def _generate_llm_response(self, prompt: str, session_id: Optional[str] = None) -> str:
        """
        Generate a response using an LLM based on the prompt and conversation history.
        
        Args:
            prompt: The user's input text
            session_id: The session identifier for accessing the conversation history
            
        Returns:
            Generated response text
        """
        # First validate if the input is a number to ensure the LLM is only used for numbers
        if not self.is_valid_number(prompt):
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
            system_message: Message = {"role": "system", "content": system_content}
            
            # Build messages list
            messages: List[Message] = [system_message]
            
            # Get session state if session_id is provided
            if session_id:
                state = self.session_repository.get_session(session_id)
                
                # Add conversation history if we have it
                if state.history:
                    # Convert Pydantic models to dictionaries for the AI client
                    for msg in state.history:
                        # Convert from domain Message to dict Message
                        messages.append({"role": msg.role, "content": msg.content})
            
            # Add the current user message
            user_message: Message = {"role": "user", "content": prompt}
            messages.append(user_message)
            
            # Log the messages being sent to the LLM for debugging
            print(f"[LLM Request] Session: {session_id}, Messages: {json.dumps(messages, indent=2)}")
            
            # Call generate_response through the AI client
            response = self.ai_client.generate_response(messages=messages)
            print(f"[LLM Response] Session: {session_id}, Response: {response}")
            
            # Update session state if we have a session ID
            if session_id and response:
                state = self.session_repository.get_session(session_id)
                
                # Create a new history list if needed
                if not state.history:
                    # If this is the first interaction, make sure to include the system message
                    state.history = [DomainMessage(role="system", content=system_content)]
                
                # Add the user message and assistant response to history
                state.history.append(DomainMessage(role="user", content=prompt))
                state.history.append(DomainMessage(role="assistant", content=response.strip()))
                
                # Limit history to the last 4 messages (2 exchanges) to keep context minimal
                if len(state.history) > 5:  # system message + 2 exchanges
                    state.history = [state.history[0]] + state.history[-4:]
                
                # Also update last_response for backward compatibility
                state.last_response = response.strip()
                
                # Save the updated session state
                self.session_repository.save_session(session_id, state)
                
                # Log the updated session state
                print(f"[Session State] Session: {session_id}, History length: {len(state.history)}")
            
            return response.strip() if response else "No response generated"
            
        except Exception as e:
            print(f"Error generating LLM response: {str(e)}")
            return f"I encountered an issue: {str(e)}" 