import logging
from pathlib import Path
from ai.gemini_client import GeminiClient
from ai.prompt_manager import PromptManager
from ai.conversation_memory import ConversationMemory
from ai.schemas import BASE_SCHEMA, CHAT_SCHEMA, VISION_ANALYSIS_SCHEMA, VISION_CHAT_SCHEMA

logger = logging.getLogger(__name__)

_VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
_MIME_MAP = {
    ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
    ".png": "image/png", ".gif": "image/gif",
    ".bmp": "image/bmp", ".webp": "image/webp",
}

# Keywords that strongly suggest the user wants Aura to look at something visually
_VISION_TRIGGERS = {
    "what do you see", "what can you see", "what's in front",
    "what is in front", "look at", "look around", "take a look",
    "describe what you see", "what's around", "what is around",
    "what's there", "what is there", "can you see", "see anything",
    "what am i holding", "what's on the", "what is on the",
    "how many people", "is there a", "is there an", "are there any",
    "describe the scene", "what's happening", "what is happening",
    "analyze this", "analyse this", "what color", "what colour",
    "show me", "tell me what you see",
}


class AIEngine:

    def __init__(self) -> None:
        self.llm = GeminiClient()
        self.memory = ConversationMemory(max_turns=10)

    # ── Public API ────────────────────────────────────────────────────────────

    def needs_vision(self, text: str) -> bool:
        """
        Return True if the user's text suggests they want Aura to look
        at something via the camera before answering.

        Checks against a keyword set — fast, no LLM call needed.
        """
        lower = text.lower()
        return any(trigger in lower for trigger in _VISION_TRIGGERS)

    async def process(self, user_input: str) -> dict:
        """Classify intent from user input and return structured result."""
        prompt = PromptManager.build_prompt(
            mode="general_control",
            task="intent",
            schema=BASE_SCHEMA,
            user_input=user_input,
        )
        return await self.llm.generate(prompt)

    async def chat(self, user_message: str) -> dict:
        """
        Conversational response, with rolling memory of recent turns.
        Automatically saves user message and assistant reply to memory.
        """
        history = self.memory.as_prompt_block()

        prompt = PromptManager.build_prompt(
            mode="chat_assistant",
            task="general_chat",
            schema=CHAT_SCHEMA,
            user_input=user_message,
            history=history,
        )
        result = await self.llm.generate(prompt)

        # Save turn to memory
        self.memory.add("user", user_message)
        reply = result.get("message") or result.get("response") or ""
        if reply:
            self.memory.add("assistant", str(reply))

        return result

    async def analyze_vision(self, image_path: str, user_query: str = "") -> dict:
        """
        Analyse an image with full detail.
        Image bytes are sent directly to Gemini multimodal API.
        """
        image_bytes, mime_type = self._read_image(image_path)
        if image_bytes is None:
            return {"error": "Failed to read image", "image_path": image_path}

        prompt = PromptManager.build_prompt(
            mode="vision_specialist",
            task="vision_analysis",
            schema=VISION_ANALYSIS_SCHEMA,
            user_input=user_query or "Analyse this image in detail.",
        )
        return await self.llm.generate(prompt, image_bytes=image_bytes, image_mime_type=mime_type)

    async def chat_with_vision(self, image_path: str, user_message: str) -> dict:
        """
        Conversational response about an image, with memory context.
        Image bytes are sent directly to Gemini multimodal API.
        """
        image_bytes, mime_type = self._read_image(image_path)
        if image_bytes is None:
            return {"error": "Failed to read image", "image_path": image_path}

        history = self.memory.as_prompt_block()

        prompt = PromptManager.build_prompt(
            mode="vision_chat_specialist",
            task="vision_chat",
            schema=VISION_CHAT_SCHEMA,
            user_input=user_message,
            history=history,
        )
        result = await self.llm.generate(prompt, image_bytes=image_bytes, image_mime_type=mime_type)

        # Save to memory
        self.memory.add("user", user_message)
        reply = result.get("response") or result.get("answer") or result.get("message") or ""
        if reply:
            self.memory.add("assistant", str(reply))

        return result

    # ── Internal ──────────────────────────────────────────────────────────────

    def _read_image(self, image_path: str) -> tuple[bytes | None, str]:
        """Read raw image bytes and return (bytes, mime_type), or (None, '') on failure."""
        try:
            path = Path(image_path)
            if not path.exists():
                logger.error("Image not found: %s", image_path)
                return None, ""
            ext = path.suffix.lower()
            if ext not in _VALID_EXTENSIONS:
                logger.error("Unsupported image format: %s", ext)
                return None, ""
            return path.read_bytes(), _MIME_MAP.get(ext, "image/jpeg")
        except Exception as exc:
            logger.error("Failed to read image %s: %s", image_path, exc)
            return None, ""
