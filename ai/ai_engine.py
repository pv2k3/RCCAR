import base64
from pathlib import Path
from ai.gemini_client import GeminiClient
from ai.prompt_manager import PromptManager
from ai.schemas import BASE_SCHEMA, CHAT_SCHEMA, VISION_ANALYSIS_SCHEMA, VISION_CHAT_SCHEMA


class AIEngine:

    def __init__(self):
        self.llm = GeminiClient()

    async def process(self, user_input: str):
        """
        General process - classifies intent and processes input.
        """
        # Step 1: Intent classification
        prompt = PromptManager.build_prompt(
            mode="general_control",
            task="intent",
            schema=BASE_SCHEMA,
            user_input=user_input
        )

        result = await self.llm.generate(prompt)

        return result

    async def chat(self, user_message: str):
        """
        Simple chat function - responds to user messages conversationally.
        
        Args:
            user_message: The user's chat message
            
        Returns:
            Dictionary with chat response
        """
        prompt = PromptManager.build_prompt(
            mode="chat_assistant",
            task="general_chat",
            schema=CHAT_SCHEMA,
            user_input=user_message
        )

        result = await self.llm.generate(prompt)
        return result

    async def analyze_vision(self, image_path: str, user_query: str = ""):
        """
        Analyze an image and provide detailed observations.
        
        Args:
            image_path: Path to the image file
            user_query: Optional question about the image
            
        Returns:
            Dictionary with vision analysis
        """
        # Read and encode image
        image_data = self._encode_image(image_path)
        
        if not image_data:
            return {
                "error": "Failed to process image",
                "image_path": image_path
            }

        prompt = PromptManager.build_prompt(
            mode="vision_specialist",
            task="vision_analysis",
            schema=VISION_ANALYSIS_SCHEMA,
            user_input=user_query if user_query else "Analyze this image in detail.",
            image_data=image_data
        )

        result = await self.llm.generate(prompt)
        return result

    async def chat_with_vision(self, image_path: str, user_message: str):
        """
        Chat about an image - combine vision analysis with conversation.
        
        Args:
            image_path: Path to the image file
            user_message: User's question or comment about the image
            
        Returns:
            Dictionary with vision-aware response
        """
        # Read and encode image
        image_data = self._encode_image(image_path)
        
        if not image_data:
            return {
                "error": "Failed to process image",
                "image_path": image_path
            }

        prompt = PromptManager.build_prompt(
            mode="vision_chat_specialist",
            task="vision_chat",
            schema=VISION_CHAT_SCHEMA,
            user_input=user_message,
            image_data=image_data
        )

        result = await self.llm.generate(prompt)
        return result

    def _encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64 encoded string, or empty string if failed
        """
        try:
            path = Path(image_path)
            
            if not path.exists():
                print(f"❌ Image not found: {image_path}")
                return ""
            
            # Check if it's a valid image file
            valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
            if path.suffix.lower() not in valid_extensions:
                print(f"❌ Invalid image format: {path.suffix}")
                return ""
            
            with open(path, "rb") as image_file:
                encoded = base64.standard_b64encode(image_file.read()).decode("utf-8")
                return encoded
                
        except Exception as e:
            print(f"❌ Error encoding image: {e}")
            return ""