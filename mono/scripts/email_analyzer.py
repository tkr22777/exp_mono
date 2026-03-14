from src.modules.llms.gemini_client import GeminiClient
from scripts.prompts import EMAIL_IMPORTANCE_PROMPT

MAX_BODY_CHARS = 1000


def analyze_email(email: dict) -> str:
    """Return a Gemini verdict for a single email (IMPORTANT / NEUTRAL / SPAM)."""
    prompt = EMAIL_IMPORTANCE_PROMPT.format(
        from_=email["from"],
        subject=email["subject"],
        date=email["date"],
        body=email["body"][:MAX_BODY_CHARS],
    )
    client = GeminiClient()
    return client.ask(prompt)
