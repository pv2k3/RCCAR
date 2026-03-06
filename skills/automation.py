"""
Automation skills — file operations, process management, timers.
"""

import asyncio
import logging
import os
import subprocess
from pathlib import Path

from core.event_bus import EventBus, Event, EventType
from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class TimerSkill(BaseSkill):
    """Set a countdown timer and announce when done."""

    @property
    def name(self) -> str:
        return "timer"

    @property
    def description(self) -> str:
        return "Set a countdown timer for a specified number of seconds."

    @property
    def triggers(self) -> list[str]:
        return ["set_timer", "timer"]

    async def execute(self, parameters: dict) -> dict:
        seconds = int(parameters.get("duration", parameters.get("seconds", 10)))

        async def _countdown():
            await asyncio.sleep(seconds)
            await self.bus.publish(Event(
                EventType.TTS_SPEAK,
                {"text": f"Timer done! {seconds} seconds elapsed."},
                source="timer_skill",
            ))

        asyncio.create_task(_countdown())
        logger.info("Timer started: %ds", seconds)
        return {"success": True, "message": f"Timer set for {seconds} seconds."}


class ListFilesSkill(BaseSkill):
    """List files in a directory."""

    @property
    def name(self) -> str:
        return "list_files"

    @property
    def description(self) -> str:
        return "List files in a given directory path."

    @property
    def triggers(self) -> list[str]:
        return ["list_files", "show_files"]

    async def execute(self, parameters: dict) -> dict:
        directory = parameters.get("path", os.getcwd())
        try:
            files = [f.name for f in Path(directory).iterdir()]
            return {"success": True, "message": f"Found {len(files)} items.", "files": files}
        except Exception as exc:
            return {"success": False, "message": str(exc)}


class RunCommandSkill(BaseSkill):
    """
    Execute a safe shell command.
    Only allows a whitelist of non-destructive commands.
    """

    ALLOWED_COMMANDS = {"echo", "date", "hostname", "whoami", "pwd", "ls", "dir"}

    @property
    def name(self) -> str:
        return "run_command"

    @property
    def description(self) -> str:
        return "Run a whitelisted shell command and return its output."

    @property
    def triggers(self) -> list[str]:
        return ["run_command", "execute_command"]

    async def execute(self, parameters: dict) -> dict:
        command = parameters.get("command", "").strip()
        base_cmd = command.split()[0] if command else ""

        if base_cmd not in self.ALLOWED_COMMANDS:
            return {
                "success": False,
                "message": f"Command '{base_cmd}' is not allowed for safety reasons.",
            }

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=10
                ),
            )
            return {
                "success": result.returncode == 0,
                "message": result.stdout.strip() or result.stderr.strip(),
            }
        except Exception as exc:
            return {"success": False, "message": str(exc)}
