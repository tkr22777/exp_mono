"""
Integration tests for text transformation functionality.
"""
import uuid

import pytest

from src.modules.llms.ai_client import AIClient
from src.modules.text_processor.repositories.memory_repositories import (
    InMemorySessionRepository,
)
from src.modules.text_processor.service import TextProcessorService


class TestTextTransformationIntegration:
    """Integration tests for the text transformation service."""

    @pytest.fixture
    def service(self):
        """Create a real service with real dependencies for integration testing."""
        session_repo = InMemorySessionRepository()
        ai_client = AIClient()
        return TextProcessorService(session_repo, ai_client)

    @pytest.fixture
    def session_id(self):
        """Generate a unique session ID for each test."""
        return str(uuid.uuid4())

    def test_text_transformation_flow(self, service, session_id):
        """Test the complete text transformation flow."""
        # Step 1: Establish initial text state
        result1 = service.process_text("a bright blue cow", session_id)
        assert "blue cow" in result1.response.lower()

        # Step 2: Apply color transformation
        result2 = service.process_text("make it red", session_id)
        assert "red" in result2.response.lower()
        assert "cow" in result2.response.lower()
        assert "blue" not in result2.response.lower()

        # Step 3: Apply animal transformation
        result3 = service.process_text("make it a pig instead", session_id)
        assert "pig" in result3.response.lower()
        assert "red" in result3.response.lower()
        assert "cow" not in result3.response.lower()

    def test_pluralization_transformation(self, service, session_id):
        """Test pluralization transformation."""
        # Establish initial state
        service.process_text("a red cat", session_id)

        # Apply pluralization
        result = service.process_text("make it plural", session_id)
        assert any(plural in result.response.lower() for plural in ["cats", "red cats"])

    def test_multiple_attribute_changes(self, service, session_id):
        """Test multiple sequential attribute changes."""
        # Start with a complex description
        service.process_text("a small brown dog", session_id)

        # Change size
        result1 = service.process_text("make it large", session_id)
        assert any(size in result1.response.lower() for size in ["large", "big"])
        assert "dog" in result1.response.lower()

        # Change color while keeping size
        result2 = service.process_text("make it white", session_id)
        assert "white" in result2.response.lower()
        assert "dog" in result2.response.lower()
        assert any(size in result2.response.lower() for size in ["large", "big"])

    def test_session_isolation(self, service):
        """Test that different sessions maintain separate text states."""
        session1 = str(uuid.uuid4())
        session2 = str(uuid.uuid4())

        # Set different initial states
        result1a = service.process_text("a blue elephant", session1)
        result2a = service.process_text("a green frog", session2)

        # Apply transformations to each session
        result1b = service.process_text("make it red", session1)
        result2b = service.process_text("make it yellow", session2)

        # Verify session isolation
        assert "elephant" in result1b.response.lower()
        assert "red" in result1b.response.lower()
        assert "frog" in result2b.response.lower()
        assert "yellow" in result2b.response.lower()

        # Ensure no cross-contamination
        assert "frog" not in result1b.response.lower()
        assert "elephant" not in result2b.response.lower()

    def test_complex_transformation_instructions(self, service, session_id):
        """Test complex transformation instructions."""
        # Start with simple text
        service.process_text("a car", session_id)

        # Apply complex transformation
        result = service.process_text("make it a fast red sports car", session_id)

        assert "red" in result.response.lower()
        assert "car" in result.response.lower()
        assert any(
            descriptor in result.response.lower()
            for descriptor in ["fast", "sport", "quick"]
        )

    def test_empty_and_invalid_inputs(self, service, session_id):
        """Test handling of empty and invalid inputs."""
        # Empty input
        result_empty = service.process_text("", session_id)
        assert "provide some text" in result_empty.response.lower()

        # Whitespace only
        result_whitespace = service.process_text("   ", session_id)
        assert "provide some text" in result_whitespace.response.lower()

        # Valid input after invalid ones should still work
        result_valid = service.process_text("a happy bird", session_id)
        assert "bird" in result_valid.response.lower()

    def test_transformation_instruction_as_first_message(self, service, session_id):
        """Test handling transformation instruction as first message without established state."""
        # Send transformation instruction as first message
        result = service.process_text("make it purple", session_id)

        # Should ask for text to establish state
        assert any(
            phrase in result.response.lower()
            for phrase in [
                "provide some text",
                "establish",
                "initial state",
                "text to work with",
            ]
        )

    def test_ambiguous_first_message_handling(self, service, session_id):
        """Test handling of ambiguous first messages like 'with double e'."""
        # Send ambiguous instruction as first message
        result = service.process_text("with double e", session_id)

        # Should ask for clarification or text to establish state
        assert any(
            phrase in result.response.lower()
            for phrase in [
                "provide some text",
                "establish",
                "initial state",
                "text to work with",
            ]
        )

    def test_two_step_transformation_process(self, service, session_id):
        """Test that the two-step process (intent analysis + transformation execution) works correctly."""
        # Establish initial state
        result1 = service.process_text("a tiny green butterfly", session_id)
        assert "green butterfly" in result1.response.lower()

        # Test complex transformation that should benefit from two-step process
        result2 = service.process_text(
            "make it huge and change color to bright orange", session_id
        )

        # Verify transformation was applied correctly
        assert "butterfly" in result2.response.lower()  # Object preserved
        assert "orange" in result2.response.lower()  # Color changed
        assert any(
            size in result2.response.lower() for size in ["huge", "large", "big"]
        )  # Size changed
        assert "green" not in result2.response.lower()  # Old color removed
        assert "tiny" not in result2.response.lower()  # Old size removed

    def test_intent_analysis_with_current_text(self, service, session_id):
        """Test that intent analysis can see and work with current text state."""
        # Establish a specific state that requires context awareness
        result1 = service.process_text(
            "a red sports car with racing stripes", session_id
        )
        assert "red sports car" in result1.response.lower()
        assert "racing stripes" in result1.response.lower()

        # Apply transformation that requires understanding current attributes
        result2 = service.process_text(
            "remove the stripes but keep it sporty", session_id
        )

        # Verify the transformation understood the context
        assert "car" in result2.response.lower()  # Object preserved
        assert "sport" in result2.response.lower()  # Sporty nature preserved
        assert "red" in result2.response.lower()  # Color preserved
        assert "stripe" not in result2.response.lower()  # Stripes removed
