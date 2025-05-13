#!/usr/bin/env python3
"""
Simple Python Experiment

A CLI application that processes text using a two-step approach:
1. Create a plan based on the text
2. Execute the plan with AI assistance

Optional third step:
3. Process with LangChain for multi-step decision making with database persistence
"""
from typing import Optional

import click

from src.modules.langchain_agent.api import (
    DecisionChain,
    LangChainDecisionResult,
    process_with_langchain,
)
from src.modules.langchain_agent.persistence.api import (
    PersistentLangChainAgent,
    create_persistent_agent,
    get_recent_chains,
)
from src.modules.planner.plan_creator import ProcessingPlan
from src.modules.text_processor.processor import ProcessingResult, process_text


def display_plan(plan: ProcessingPlan) -> None:
    """
    Display the processing plan in a formatted way.

    Args:
        plan: The processing plan to display
    """
    click.echo("\n🔍 STEP 1: PLAN CREATED")
    click.echo(f"Title: {plan.title}")
    click.echo(f"Status: {plan.status}")


def display_results(results: ProcessingResult) -> None:
    """
    Display the processing results in a formatted way.

    Args:
        results: The processing results to display
    """
    click.echo("\n⚙️ STEP 2: PLAN EXECUTED")
    click.echo(f"Title: {results.title}")
    click.echo(f"Status: {results.status}")

    click.echo("\n🤖 AI RESPONSE:")
    click.echo(f"{results.ai_response}")


def display_langchain_results(
    chain: DecisionChain, result: LangChainDecisionResult
) -> None:
    """
    Display the LangChain decision-making results in a formatted way.

    Args:
        chain: The full decision chain
        result: The simplified results
    """
    click.echo("\n🔗 STEP 3: LANGCHAIN DECISION PROCESS")
    click.echo(f"Chain ID: {result.chain_id}")
    click.echo(f"Title: {result.title}")
    click.echo(f"Steps: {result.step_count}")

    # Display each step in the decision process
    for i, step in enumerate(chain.steps, 1):
        click.echo(f"\n📌 Decision Step {i}:")
        click.echo(f"  Reasoning: {step.reasoning}")
        click.echo(f"  Decision: {step.decision}")
        if step.next_actions:
            click.echo(f"  Next Actions: {', '.join(step.next_actions)}")

    click.echo(f"\n🎯 FINAL DECISION:")
    click.echo(f"{result.final_decision}")


def display_recent_chains(limit: int = 5) -> None:
    """
    Display recent decision chains from the database.

    Args:
        limit: Maximum number of chains to display
    """
    chains = get_recent_chains(limit=limit)

    if not chains:
        click.echo("\n📝 No recent decision chains found.")
        return

    click.echo(f"\n📝 RECENT DECISION CHAINS ({len(chains)}):")
    for i, chain in enumerate(chains, 1):
        click.echo(f"{i}. {chain.title} (ID: {chain.chain_id[:8]}...)")
        click.echo(f"   Status: {chain.status}")
        click.echo(f"   Steps: {len(chain.steps)}")
        if chain.final_decision:
            decision_preview = (
                chain.final_decision[:50] + "..."
                if len(chain.final_decision) > 50
                else chain.final_decision
            )
            click.echo(f"   Decision: {decision_preview}")
        click.echo("")


@click.command()
@click.option("--name", default="World", help="Who to greet")
@click.option("--text", help="Text to process")
@click.option(
    "--use-langchain", is_flag=True, help="Whether to use LangChain for decision making"
)
@click.option(
    "--persist", is_flag=True, help="Whether to persist decisions to database"
)
@click.option(
    "--list-recent", is_flag=True, help="List recent decision chains from database"
)
@click.option("--chain-id", help="Load a specific decision chain by ID")
def main(
    name: str,
    text: Optional[str],
    use_langchain: bool,
    persist: bool,
    list_recent: bool,
    chain_id: Optional[str],
) -> int:
    """Process text using a two-step approach with AI assistance."""
    click.echo(f"Hello {name}!")

    # List recent chains if requested
    if list_recent:
        display_recent_chains()
        return 0

    # Load a specific chain if requested
    if chain_id:
        click.echo(f"\nLoading decision chain {chain_id}...")
        try:
            agent = create_persistent_agent()
            chain = agent.load_chain(chain_id)

            if chain:
                result = LangChainDecisionResult(
                    title=chain.title,
                    final_decision=chain.final_decision or "No final decision",
                    step_count=len(chain.steps),
                    context=chain.context,
                    chain_id=chain.chain_id,
                )
                display_langchain_results(chain, result)
            else:
                click.echo(f"❌ Chain with ID {chain_id} not found.")
        except Exception as e:
            click.echo(f"\n❌ Error loading chain: {e}")

        return 0

    if text:
        click.echo("\nProcessing text...")
        plan, results = process_text(text)
        display_plan(plan)
        display_results(results)

        if use_langchain:
            click.echo("\nProcessing with LangChain...")
            try:
                if persist:
                    # Use the persistent agent
                    agent = create_persistent_agent()
                    chain, chain_id = agent.process_text_with_persistence(text)

                    result = LangChainDecisionResult(
                        title=chain.title,
                        final_decision=chain.final_decision or "No final decision",
                        step_count=len(chain.steps),
                        context=chain.context,
                        chain_id=chain.chain_id,
                    )

                    click.echo(f"\n💾 Decision chain saved with ID: {chain_id}")
                    display_langchain_results(chain, result)
                else:
                    # Use the standard non-persistent agent
                    chain, langchain_results = process_with_langchain(text)
                    display_langchain_results(chain, langchain_results)
            except Exception as e:
                click.echo(f"\n❌ Error processing with LangChain: {e}")
                click.echo(
                    "Make sure you have installed langchain and related dependencies."
                )

    return 0


if __name__ == "__main__":
    main()  # type: ignore
