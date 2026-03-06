"""
Base class for all Aura skills.
Every skill must implement name, description, triggers, and execute().
"""

from abc import ABC, abstractmethod
from core.event_bus import EventBus


class BaseSkill(ABC):
    """
    Abstract base for modular skills.

    A skill is a self-contained capability triggered by an intent.
    Each skill subscribes to relevant events or is called by the controller.
    """

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique skill identifier (e.g. 'capture')."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what this skill does."""

    @property
    @abstractmethod
    def triggers(self) -> list[str]:
        """List of intent names that activate this skill."""

    @abstractmethod
    async def execute(self, parameters: dict) -> dict:
        """
        Run the skill logic.

        Args:
            parameters: Intent-extracted parameters from the LLM.

        Returns:
            Result dict with at minimum {"success": bool, "message": str}.
        """
