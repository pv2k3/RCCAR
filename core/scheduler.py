"""
Aura Scheduler — runs periodic background tasks.

Each task is an async coroutine that fires on a fixed interval.
"""

import asyncio
import logging
from dataclasses import dataclass
from typing import Callable, Coroutine

logger = logging.getLogger(__name__)


@dataclass
class PeriodicTask:
    """Definition of a repeating background task."""

    name: str
    coroutine_fn: Callable[[], Coroutine]
    interval_seconds: float


class Scheduler:
    """
    Runs multiple periodic async tasks concurrently.

    Usage:
        scheduler = Scheduler()
        scheduler.add(PeriodicTask("health_check", check_fn, interval_seconds=10))
        await scheduler.run()   # runs until stop() is called
    """

    def __init__(self) -> None:
        self._tasks: list[PeriodicTask] = []
        self._running = False
        self._handles: list[asyncio.Task] = []

    def add(self, task: PeriodicTask) -> None:
        """Register a periodic task."""
        self._tasks.append(task)
        logger.debug("Scheduled task '%s' every %.1fs", task.name, task.interval_seconds)

    async def run(self) -> None:
        """Start all periodic tasks as concurrent asyncio tasks."""
        self._running = True
        self._handles = [
            asyncio.create_task(self._loop(task), name=task.name)
            for task in self._tasks
        ]
        logger.info("Scheduler running %d task(s).", len(self._tasks))
        await asyncio.gather(*self._handles, return_exceptions=True)

    async def _loop(self, task: PeriodicTask) -> None:
        """Repeatedly call a task's coroutine at its interval."""
        logger.info("Periodic task started: %s", task.name)
        while self._running:
            try:
                await task.coroutine_fn()
            except asyncio.CancelledError:
                break
            except Exception as exc:
                logger.error("Task '%s' raised: %s", task.name, exc, exc_info=True)
            await asyncio.sleep(task.interval_seconds)

    def stop(self) -> None:
        """Cancel all running tasks."""
        self._running = False
        for handle in self._handles:
            handle.cancel()
        logger.info("Scheduler stopped.")
