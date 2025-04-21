#!/usr/bin/env python3
"""
Simple Python Experiment

A CLI application that processes text using a two-step approach:
1. Create a plan based on the text
2. Execute the plan with AI assistance
"""
from typing import Optional

import click

from src.plan_creator import ProcessingPlan
from src.text_processor import ProcessingResult, process_text


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

    # Display AI response
    click.echo("\n🤖 AI RESPONSE:")
    click.echo(f"{results.ai_response}")


@click.command()
@click.option("--name", default="World", help="Who to greet")
@click.option("--text", help="Text to process")
def main(name: str, text: Optional[str]) -> int:
    """Process text using a two-step approach with AI assistance."""
    click.echo(f"Hello {name}!")

    if text:
        click.echo("\nProcessing text...")

        # Process text using the two-step approach
        plan, results = process_text(text)

        # Display the plan and results
        display_plan(plan)
        display_results(results)

    return 0


if __name__ == "__main__":
    main()  # type: ignore
