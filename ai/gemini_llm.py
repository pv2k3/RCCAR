import asyncio
import json
import re
import os
from typing import Dict

import google.generativeai as genai
from dotenv import load_dotenv


load_dotenv()


class GeminiLLM:

    def __init__(
        self,
        model_name: str = "gemini-pro",
        temperature: float = 0.2,
        max_retries: int = 2
    ):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not found in .env")

        try:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model_name)
        except Exception as e:
            raise RuntimeError(f"Gemini initialization failed: {e}")

        self.temperature = temperature
        self.max_retries = max_retries

    async def generate(self, prompt: str) -> Dict:

        loop = asyncio.get_running_loop()

        for _ in range(self.max_retries + 1):
            try:
                response = await loop.run_in_executor(
                    None,
                    lambda: self.model.generate_content(
                        prompt,
                        generation_config={
                            "temperature": self.temperature
                        }
                    )
                )

                text = response.text.strip()
                parsed = self._safe_json_parse(text)

                if parsed:
                    return parsed

            except Exception as e:
                raise RuntimeError(f"Gemini call failed: {e}")

        raise RuntimeError("Failed to parse valid JSON from Gemini.")

    def _safe_json_parse(self, text: str) -> Dict | None:
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