import asyncio
import json
import re
import os
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
import google.generativeai as genai
from ai.llm_interface import LLMInterface
from config.settings import settings


class GeminiClient(LLMInterface):

    def __init__(self) -> None:
        api_key = settings.gemini_api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY missing from .env")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self.temperature = settings.llm_temperature
        self.max_retries = settings.llm_max_retries

    async def generate(
        self,
        prompt: str,
        image_bytes: bytes | None = None,
        image_mime_type: str = "image/jpeg",
    ) -> dict:
        """
        Send a prompt to Gemini and return a parsed JSON dict.

        For multimodal calls, pass image_bytes — the SDK will handle
        the proper content format (text + inline image data).
        """
        loop = asyncio.get_running_loop()

        # Multimodal: list of [text, inline_image_part]
        # Text-only: plain string
        if image_bytes:
            content = [prompt, {"mime_type": image_mime_type, "data": image_bytes}]
        else:
            content = prompt

        for _ in range(self.max_retries + 1):
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(
                    content,
                    generation_config={"temperature": self.temperature},
                ),
            )

            parsed = self._safe_parse(response.text)
            if parsed is not None:
                return parsed

        raise RuntimeError("Failed to parse a valid JSON response from Gemini.")

    def _safe_parse(self, text: str) -> dict | None:
        """Try JSON parse; fall back to regex extraction of first JSON object."""
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None