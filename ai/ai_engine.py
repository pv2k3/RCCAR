from ai.gemini_client import GeminiClient
from ai.prompt_manager import PromptManager
from ai.schemas import BASE_SCHEMA


class AIEngine:

    def __init__(self):
        self.llm = GeminiClient()

    async def process(self, user_input: str):

        # Step 1: Intent classification
        prompt = PromptManager.build_prompt(
            mode="general_control",
            task="intent",
            schema=BASE_SCHEMA,
            user_input=user_input
        )

        result = await self.llm.generate(prompt)

        return result