"""
LangChain Agent Module

This module implements a decision-making agent using LangChain.
It supports multi-step reasoning and can be extended with persistence capabilities.
"""
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

from langchain.agents import AgentExecutor, create_react_agent
from langchain.chains import LLMChain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain.prompts import PromptTemplate
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.language_models import BaseLanguageModel
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from src.llms.ai_client import default_client
from src.utils.settings import settings


class DecisionStep(BaseModel):
    """Model representing a single step in the decision process."""

    step_id: str = Field(default_factory=lambda: str(uuid4()))
    step_number: int = Field(description="The sequence number of this step")
    reasoning: str = Field(description="The reasoning behind this step")
    decision: str = Field(description="The decision made in this step")
    next_actions: List[str] = Field(
        default_factory=list, description="Next actions to take based on this decision"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata for this step"
    )


class DecisionChain(BaseModel):
    """Model representing a chain of decision steps."""

    chain_id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(description="Title for this decision chain")
    context: str = Field(description="The context that prompted this decision chain")
    steps: List[DecisionStep] = Field(
        default_factory=list, description="The steps in this decision chain"
    )
    final_decision: Optional[str] = Field(
        None, description="The final decision reached at the end of the chain"
    )
    status: str = Field(
        default="in_progress",
        description="Status of the decision chain (in_progress, completed, error)",
    )


class LangChainAgent:
    """Agent for multi-step decision making using LangChain."""

    def __init__(
        self,
        llm: Optional[BaseLanguageModel] = None,
        verbose: bool = False,
    ):
        """
        Initialize the LangChain decision-making agent.

        Args:
            llm: The language model to use (defaults to OpenAI model from settings)
            verbose: Whether to print verbose output during execution
        """
        # Use the provided LLM or create a new one based on settings
        self.llm = llm or ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model_name=settings.MODEL_NAME,
            temperature=settings.TEMPERATURE,
        )
        self.verbose = verbose
        
        # Create a message history for the agent
        self.message_history = ChatMessageHistory()
        
        # Create the React agent with tools
        self.agent = self._create_agent()
        
        # Active decision chain
        self.active_chain: Optional[DecisionChain] = None

    def _create_agent(self) -> AgentExecutor:
        """
        Create a React agent with tools for decision making.
        
        Returns:
            An AgentExecutor instance
        """
        # For simplicity, we're not using tools in this initial implementation
        # This can be extended with custom tools in future versions
        tools = []
        
        # Create a prompt template for the agent
        prompt = PromptTemplate.from_template(
            """You are a decision-making agent that helps with complex problems.
            
            {tools}
            
            Context: {context}
            
            Think through this step-by-step:
            1. Analyze the context carefully
            2. Identify key decision points
            3. Evaluate options for each decision
            4. Make recommendations based on your analysis
            
            {chat_history}
            
            Human: {input}
            {agent_scratchpad}
            
            Available tools: {tool_names}
            """
        )
        
        # Create the agent
        agent = create_react_agent(self.llm, tools, prompt)
        
        # Create the agent executor
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=self.verbose,
            handle_parsing_errors=True,
        )

    def create_decision_chain(self, context: str, title: Optional[str] = None) -> DecisionChain:
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
            title = default_client.generate_response(prompt).strip()
        
        # Create a new decision chain
        self.active_chain = DecisionChain(
            title=title,
            context=context,
            steps=[],
        )
        
        return self.active_chain
    
    def add_decision_step(
        self, reasoning: str, decision: str, next_actions: List[str], metadata: Dict[str, Any] = None
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
            raise ValueError("No active decision chain. Call create_decision_chain first.")
        
        step_number = len(self.active_chain.steps) + 1
        step = DecisionStep(
            step_number=step_number,
            reasoning=reasoning,
            decision=decision,
            next_actions=next_actions,
            metadata=metadata or {},
        )
        
        self.active_chain.steps.append(step)
        return step
    
    def complete_decision_chain(self, final_decision: str) -> DecisionChain:
        """
        Complete the active decision chain with a final decision.
        
        Args:
            final_decision: The final decision reached
            
        Returns:
            The completed DecisionChain
            
        Raises:
            ValueError: If no active decision chain exists
        """
        if not self.active_chain:
            raise ValueError("No active decision chain. Call create_decision_chain first.")
        
        self.active_chain.final_decision = final_decision
        self.active_chain.status = "completed"
        
        # Return the completed chain
        completed_chain = self.active_chain
        self.active_chain = None
        return completed_chain
    
    def process_text(self, text: str) -> DecisionChain:
        """
        Process text input through a decision-making chain.
        
        Args:
            text: The input text to process
            
        Returns:
            A completed DecisionChain with the decision-making process
        """
        # Create a new decision chain
        chain = self.create_decision_chain(text)
        
        # Clear previous message history
        self.message_history.clear()
        
        # Run the agent to get an initial analysis
        if isinstance(self.agent, dict):
            initial_result = self.agent["invoke"]({"input": text, "context": text})
        else:
            initial_result = self.agent.invoke(
                {"input": text, "context": text, "chat_history": self.message_history.messages}
            )
        
        # Add the first step based on the agent's output
        reasoning = "Initial analysis of the input text"
        decision = initial_result["output"]
        next_actions = ["Refine analysis", "Consider alternatives", "Prepare final decision"]
        self.add_decision_step(reasoning, decision, next_actions)
        
        # Run a refinement step
        refinement_prompt = f"Given your initial analysis: {decision}, what refinements or alternatives should be considered?"
        if isinstance(self.agent, dict):
            refinement_result = self.agent["invoke"]({"input": refinement_prompt, "context": text})
        else:
            refinement_result = self.agent.invoke(
                {"input": refinement_prompt, "context": text, "chat_history": self.message_history.messages}
            )
        
        # Add the refinement step
        reasoning = "Refinement of initial analysis"
        decision = refinement_result["output"]
        next_actions = ["Prepare final decision"]
        self.add_decision_step(reasoning, decision, next_actions)
        
        # Generate the final decision
        final_prompt = f"Based on your analysis and refinements, what is your final decision or recommendation regarding: {text}"
        if isinstance(self.agent, dict):
            final_result = self.agent["invoke"]({"input": final_prompt, "context": text})
        else:
            final_result = self.agent.invoke(
                {"input": final_prompt, "context": text, "chat_history": self.message_history.messages}
            )
        
        # Complete the decision chain
        return self.complete_decision_chain(final_result["output"])


def create_agent() -> LangChainAgent:
    """
    Create a LangChain agent with default settings.
    
    Returns:
        A configured LangChainAgent instance
    """
    return LangChainAgent(verbose=True) 