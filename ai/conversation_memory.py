"""
Conversation memory — rolling buffer of recent turns.
Injected into prompts so Aura remembers context across exchanges.
"""

from dataclasses import dataclass, field
from collections import deque


@dataclass
class Turn:
    role: str   # "user" or "assistant"
    text: str


class ConversationMemory:
    """
    Stores the last N conversation turns.

    Usage:
        memory = ConversationMemory(max_turns=10)
        memory.add("user", "Hello!")
        memory.add("assistant", "Hi there!")
        print(memory.as_prompt_block())
    """

    def __init__(self, max_turns: int = 10) -> None:
        self._turns: deque[Turn] = deque(maxlen=max_turns * 2)  # *2 for user+assistant pairs

    def add(self, role: str, text: str) -> None:
        """Add a turn to memory."""
        if text and text.strip():
            self._turns.append(Turn(role=role, text=text.strip()))

    def as_prompt_block(self) -> str:
        """
        Format history as a readable block for injection into prompts.
        Returns empty string if no history yet.
        """
        if not self._turns:
            return ""
        lines = ["Conversation History:"]
        for turn in self._turns:
            prefix = "User" if turn.role == "user" else "Aura"
            lines.append(f"{prefix}: {turn.text}")
        return "\n".join(lines)

    def clear(self) -> None:
        """Wipe all history."""
        self._turns.clear()

    def __len__(self) -> int:
        return len(self._turns)
