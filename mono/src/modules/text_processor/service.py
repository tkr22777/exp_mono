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
        response = self._generate_llm_response(text, session_id)
        logger.info(f"Generated response: '{response}' for session: {session_id}")

        return ProcessingResult(response=response, session_id=session_id)

    def _generate_llm_response(
        self, prompt: str, session_id: Optional[str] = None
    ) -> str:
        """
        Generate text transformation response using conversation history.

        Implementation note: First input establishes the text state,
        subsequent inputs apply modifications to transform the current text.
        """
        try:
            # Create system message for text transformation behavior
            system_content = (
                "You are a text transformation assistant. Follow these rules exactly:\n"
                "1. If this is the first text in the conversation, respond with exactly that text (this establishes the current text state)\n"
                "2. For subsequent inputs, understand what changes the user wants to make to the current text and apply them\n"
                "3. Always return only the final transformed text, nothing else\n"
                "4. Pay attention to the conversation history to know what the current text state is\n"
                "5. Be smart about understanding user intent (e.g., 'make it red' should change color words, 'make it plural' should pluralize, etc.)\n"
                "6. Example: Current text: 'a bright blue cow' → User says: 'make it red' → Response: 'a bright red cow'"
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

            logger.debug(
                f"Sending request to LLM for session {session_id}: {json.dumps(messages, indent=2)}"
            )
            response = self.ai_client.generate_response(messages=messages)
            logger.debug(
                f"Received response from LLM for session {session_id}: {response}"
            )

            # Update session state if we have a session ID
            if session_id and response:
                state = self.session_repository.get_session(session_id)

                # Create a new history list if needed
                if not state.history:
                    state.history = [
                        DomainMessage(role="system", content=system_content)
                    ]

                # Add the user message and assistant response to history
                state.history.append(DomainMessage(role="user", content=prompt))
                state.history.append(
                    DomainMessage(role="assistant", content=response.strip())
                )

                # Limit history to system message + last 4 exchanges to maintain context
                if len(state.history) > 9:  # system + 4 exchanges = 9 messages
                    state.history = [state.history[0]] + state.history[-8:]

                # Update last_response for backward compatibility
                state.last_response = response.strip()
                self.session_repository.save_session(session_id, state)
                logger.debug(
                    f"Updated session state for session {session_id}, history length: {len(state.history)}"
                )

            return response.strip() if response else "No response generated"

        except AIClientError as e:
            logger.error(
                f"AI client error while generating response: {str(e)}", exc_info=True
            )
            return f"I encountered an AI processing issue: {str(e)}"
        except Exception as e:
            logger.error(
                f"Unexpected error generating LLM response: {str(e)}", exc_info=True
            )
            return f"I encountered an unexpected issue: {str(e)}"
