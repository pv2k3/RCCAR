from abc import ABC, abstractmethod


class LLMInterface(ABC):

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        image_bytes: bytes | None = None,
        image_mime_type: str = "image/jpeg",
    ) -> dict:
        """Generate a structured JSON response from the LLM."""