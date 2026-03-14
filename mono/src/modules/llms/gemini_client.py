import os

from dotenv import load_dotenv
from google import genai

load_dotenv()
load_dotenv(".env.local", override=True)

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.5-flash")


class GeminiClient:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not set. Add it to your .env.local file."
            )
        self.client = genai.Client(api_key=api_key)

    def ask(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )
        return response.text
