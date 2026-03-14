import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-1.5-flash-001")


class GeminiClient:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "GEMINI_API_KEY not set. Add it to your .env file."
            )
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(GEMINI_MODEL)

    def ask(self, prompt: str) -> str:
        response = self.model.generate_content(prompt)
        return response.text
