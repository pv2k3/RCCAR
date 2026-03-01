from abc import ABC, abstractmethod
from typing import Dict


class LLMInterface(ABC):

    @abstractmethod
    async def generate(
        self,
        user_input: str,
        task: str = "chat"
    ) -> Dict:
        """
        Generate structured JSON response.
        Must return dictionary.
        """
        pass