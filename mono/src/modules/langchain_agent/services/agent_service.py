"""
LangChain Agent Service

This module contains the business logic for the LangChain Agent.
"""

from typing import Any, Dict, List, Optional, Tuple, Union, cast

from langchain.agents import AgentExecutor, create_react_agent
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.language_models import BaseLanguageModel
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI

from src.modules.langchain_agent.models.domain import DecisionChain, DecisionStep
from src.modules.langchain_agent.repositories.interfaces import DecisionChainRepository
from src.modules.llms import AIClientError
from src.modules.llms.ai_client import default_client
from src.utils.settings import settings


class LangChainAgentService:
    """Service for multi-step decision making using LangChain."""

    def __init__(
        self,
        repository: DecisionChainRepository,
        llm: Optional[BaseLanguageModel] = None,
        verbose: bool = False,
        max_iterations: int = 5,
    ):
        """
        Initialize the LangChain decision-making agent service.

        Args:
            repository: Repository for decision chains
            llm: The language model to use (defaults to OpenAI model from settings)
            verbose: Whether to print verbose output during execution
            max_iterations: Maximum number of iterations for the agent to run
        """
        # Store repository
        self.repository = repository

        # Use the provided LLM or create a new one based on settings
        self.llm = llm or ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
        )
        self.verbose = verbose
        self.max_iterations = max_iterations

        # Create a message history for the agent
        self.message_history = ChatMessageHistory()

        # Create the React agent with tools
        self.agent = self._create_agent()

        # Active decision chain
        self.active_chain: Optional[DecisionChain] = None

    def _create_agent(self) -> Any:
        """
        Create a simple wrapper around the LLM instead of a React agent with tools.

        Returns:
            A simple object with an invoke method that calls the LLM
        """
        # Create a simple prompt template for decision making
        prompt = PromptTemplate.from_template(
            """You are a decision-making assistant that helps with complex problems.
            
            Context: {context}
            
            Think through this step-by-step:
            1. Analyze the context carefully
            2. Identify key decision points
            3. Evaluate options for each decision
            4. Make recommendations based on your analysis
            
            Provide a detailed and thoughtful response that shows your reasoning process.
            
            {chat_history}
            
            Human: {input}
            """
        )

        # Create a runnable sequence (prompt | llm) instead of using LLMChain
        runnable = prompt | self.llm

        # Create a wrapper that mimics the AgentExecutor interface but just uses the LLM
        class SimpleLLMExecutor:
            def __init__(self, runnable):
                self.runnable = runnable

            def invoke(self, input_data):
                # Extract the input and context from the input data
                input_text = input_data.get("input", "")
                context = input_data.get("context", "")
                chat_history = input_data.get("chat_history", [])

                # Call the runnable with the input data
                response = self.runnable.invoke(
                    {
                        "input": input_text,
                        "context": context,
                        "chat_history": chat_history,
                    }
                )

                # Handle case where response is an AIMessage or other message type
                if hasattr(response, "content"):
                    response = response.content

                # Return a dictionary with the output to match AgentExecutor interface
                return {"output": response}

        return SimpleLLMExecutor(runnable)

    def create_decision_chain(
        self, context: str, title: Optional[str] = None
    ) -> DecisionChain:
        """
        Create a new decision chain for the given context.

        Args:
            context: The context for the decision chain
            title: Optional title for the decision chain

        Returns:
            A new DecisionChain instance
        """
        # Generate a title if not provided
        if not title:
            prompt = f"Generate a concise title (5-7 words) for a decision process about: {context}"
            try:
                title = default_client.generate_response(prompt).strip()
            except AIClientError as e:
                # Fallback to a generic title if AI generation fails
                title = "Decision Process"

        # Create a new decision chain
        self.active_chain = DecisionChain(
            title=title,
            context=context,
            steps=[],
        )

        return self.active_chain

    def add_decision_step(
        self,
        reasoning: str,
        decision: str,
        next_actions: List[str],
        metadata: Dict[str, Any] = None,
    ) -> DecisionStep:
        """
        Add a step to the active decision chain.

        Args:
            reasoning: The reasoning behind the decision
            decision: The decision made
            next_actions: List of next actions to take
            metadata: Additional metadata for this step

        Returns:
            The newly created DecisionStep

        Raises:
            ValueError: If no active decision chain exists
        """
        if not self.active_chain:
            raise ValueError("No active decision chain")

        # Create a new step
        step = DecisionStep(
            step_number=len(self.active_chain.steps) + 1,
            reasoning=reasoning,
            decision=decision,
            next_actions=next_actions or [],
            metadata=metadata or {},
        )

        # Add the step to the active chain
        self.active_chain.steps.append(step)

        return step

    def complete_decision_chain(self, final_decision: str) -> DecisionChain:
        """
        Complete the active decision chain with a final decision.

        Args:
            final_decision: The final decision for the chain

        Returns:
            The completed decision chain

        Raises:
            ValueError: If no active decision chain exists
        """
        if not self.active_chain:
            raise ValueError("No active decision chain")

        # Update the active chain
        self.active_chain.final_decision = final_decision
        self.active_chain.status = "completed"

        return self.active_chain

    def process_text(self, text: str) -> DecisionChain:
        """
        Process text to generate a decision chain.

        Args:
            text: The input text to process

        Returns:
            The generated decision chain
        """
        # Create a new decision chain
        chain = self.create_decision_chain(context=text)

        # Reset chat history
        self.message_history.clear()

        # Initialize step counter
        step_number = 1

        # Run the agent for multiple steps
        for _ in range(self.max_iterations):
            # Generate a prompt for this step
            if step_number == 1:
                prompt = "Analyze the context and make an initial decision."
            else:
                prompt = f"Based on your previous decision, what is the next step (step {step_number})?"

            # Run the agent
            result = self.agent.invoke(
                {
                    "input": prompt,
                    "context": text,
                    "chat_history": self.message_history.messages,
                }
            )

            # Extract the output
            output = result.get("output", "")

            # Add to chat history
            self.message_history.add_user_message(prompt)
            self.message_history.add_ai_message(output)

            # Split the output into reasoning and decision
            parts = output.split("\n\n", 1)
            reasoning = parts[0]
            decision = parts[1] if len(parts) > 1 else reasoning

            # Determine next actions
            next_actions = []
            if step_number < self.max_iterations:
                next_actions = ["Continue to next step"]

            # Add the step to the chain
            self.add_decision_step(
                reasoning=reasoning,
                decision=decision,
                next_actions=next_actions,
            )

            # Increment step counter
            step_number += 1

            # Stop if we've reached the maximum number of steps
            if step_number > self.max_iterations:
                break

        # Complete the chain with a final decision
        final_decision = (
            f"After {step_number - 1} steps of analysis, "
            f"the final decision is: {chain.steps[-1].decision}"
        )
        self.complete_decision_chain(final_decision)

        return chain

    def process_text_with_persistence(self, text: str) -> Tuple[DecisionChain, str]:
        """
        Process text and persist the decision chain.

        Args:
            text: The input text to process

        Returns:
            A tuple containing the decision chain and its ID
        """
        # Process the text
        chain = self.process_text(text)

        # Save the chain
        chain_id = self.repository.save_chain(chain)

        return chain, chain_id

    def get_chain(self, chain_id: str) -> Optional[DecisionChain]:
        """
        Get a decision chain by ID.

        Args:
            chain_id: The ID of the chain to get

        Returns:
            The decision chain or None if not found
        """
        return self.repository.get_chain(chain_id)

    def get_recent_chains(self, limit: int = 10) -> List[DecisionChain]:
        """
        Get recent decision chains.

        Args:
            limit: Maximum number of chains to return

        Returns:
            List of decision chains
        """
        return self.repository.get_recent_chains(limit=limit)

    def delete_chain(self, chain_id: str) -> bool:
        """
        Delete a decision chain by ID.

        Args:
            chain_id: The ID of the chain to delete

        Returns:
            True if the chain was deleted, False otherwise
        """
        return self.repository.delete_chain(chain_id)
