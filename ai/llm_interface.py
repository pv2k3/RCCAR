from abc import ABC, abstractmethod
from typing import Dict


class LLMInterface(ABC):

    @abstractmethod
    async def generate(self, prompt: str) -> Dict:
        pass