import asyncio
import json
import re
import os
import google.generativeai as genai
from dotenv import load_dotenv
from ai.llm_interface import LLMInterface


load_dotenv()


class GeminiClient(LLMInterface):

    def __init__(
        self,
        model_name: str = "models/gemini-2.5-flash",
        temperature: float = 0.2,
        max_retries: int = 2
    ):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.temperature = temperature
        self.max_retries = max_retries

    async def generate(self, prompt: str):

        loop = asyncio.get_running_loop()

        for _ in range(self.max_retries + 1):

            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": self.temperature
                    }
                )
            )

            parsed = self._safe_parse(response.text)

            if parsed:
                return parsed

        raise RuntimeError("Failed to parse Gemini JSON response.")

    def _safe_parse(self, text):

        try:
            return json.loads(text)
        except:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    return None
        return None