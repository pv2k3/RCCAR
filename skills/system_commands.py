"""
System command skills — control OS-level features.
"""

import asyncio
import logging
import subprocess
import platform

from core.event_bus import EventBus, Event, EventType
from skills.base_skill import BaseSkill

logger = logging.getLogger(__name__)


class VolumeSkill(BaseSkill):
    """Control system volume."""

    @property
    def name(self) -> str:
        return "volume"

    @property
    def description(self) -> str:
        return "Adjust system volume up, down, or mute."

    @property
    def triggers(self) -> list[str]:
        return ["volume_up", "volume_down", "mute"]

    async def execute(self, parameters: dict) -> dict:
        direction = parameters.get("direction", "up")
        system = platform.system()

        try:
            if system == "Windows":
                from ctypes import cast, POINTER
                from comtypes import CLSCTX_ALL
                from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

                devices = AudioUtilities.GetSpeakers()
                interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(IAudioEndpointVolume))

                current = volume.GetMasterVolumeLevelScalar()
                if direction == "up":
                    volume.SetMasterVolumeLevelScalar(min(current + 0.1, 1.0), None)
                elif direction == "down":
                    volume.SetMasterVolumeLevelScalar(max(current - 0.1, 0.0), None)
                elif direction == "mute":
                    volume.SetMute(1, None)

            elif system == "Linux":
                cmd = "pactl set-sink-volume @DEFAULT_SINK@ +10%" if direction == "up" else \
                      "pactl set-sink-volume @DEFAULT_SINK@ -10%"
                subprocess.run(cmd.split(), check=True)

            logger.info("Volume skill executed: %s", direction)
            return {"success": True, "message": f"Volume {direction}"}

        except Exception as exc:
            logger.error("Volume skill failed: %s", exc)
            return {"success": False, "message": str(exc)}


class OpenApplicationSkill(BaseSkill):
    """Open a named application."""

    @property
    def name(self) -> str:
        return "open_app"

    @property
    def description(self) -> str:
        return "Open a system application by name."

    @property
    def triggers(self) -> list[str]:
        return ["open_application", "launch_app"]

    async def execute(self, parameters: dict) -> dict:
        app_name = parameters.get("application", "")
        if not app_name:
            return {"success": False, "message": "No application specified."}

        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(
                None,
                lambda: subprocess.Popen([app_name], shell=True)
            )
            logger.info("Opened application: %s", app_name)
            return {"success": True, "message": f"Opening {app_name}"}
        except Exception as exc:
            logger.error("Open app failed: %s", exc)
            return {"success": False, "message": str(exc)}


class SystemInfoSkill(BaseSkill):
    """Return basic system information."""

    @property
    def name(self) -> str:
        return "system_info"

    @property
    def description(self) -> str:
        return "Report CPU, memory, and platform information."

    @property
    def triggers(self) -> list[str]:
        return ["system_info", "system_status"]

    async def execute(self, parameters: dict) -> dict:
        try:
            import psutil
            info = {
                "platform": platform.system(),
                "cpu_percent": psutil.cpu_percent(interval=0.5),
                "memory_percent": psutil.virtual_memory().percent,
            }
            return {"success": True, "message": str(info), "data": info}
        except ImportError:
            info = {"platform": platform.system()}
            return {"success": True, "message": str(info), "data": info}
