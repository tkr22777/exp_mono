"""
Tests for the LangChainAgentService.
"""
from unittest.mock import MagicMock, patch

import pytest

from src.modules.langchain_agent.models.domain import DecisionChain
from src.modules.langchain_agent.services.agent_service import LangChainAgentService


@pytest.fixture
def mock_repository():
    """Fixture providing a mock repository."""
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_llm():
    """Fixture providing a mock language model."""
    llm = MagicMock()
    llm.invoke.return_value = {"output": "Mock LLM response"}
    return llm


class TestLangChainAgentService:
    """Tests for the LangChainAgentService class."""

    def test_process_text_with_persistence(self, mock_repository, mock_llm):
        """Test processing text with persistence."""
        # Arrange
        service = LangChainAgentService(repository=mock_repository, llm=mock_llm)

        # Mock the process_text method
        sample_chain = DecisionChain(
            title="Test Chain",
            context="Test context",
            steps=[],
            final_decision="Test decision",
            status="completed",
        )
        mock_repository.save_chain.return_value = "test-chain-id"

        # Create a patch for the process_text method
        with patch.object(service, "process_text", return_value=sample_chain):
            # Act
            chain, chain_id = service.process_text_with_persistence("Test input")

            # Assert
            assert chain == sample_chain
            assert chain_id == "test-chain-id"
            mock_repository.save_chain.assert_called_once_with(sample_chain)
