"""
Aura — main entry point.

Boots all services in order:
  1. Config & logging
  2. Event bus
  3. Controller
  4. Navigator (robotics)
  5. Vision service
  6. Voice service
  7. LLM service
  8. API server (optional)
  9. Scheduler
"""

import asyncio
import logging
import signal
import sys

from config.settings import settings
from core.event_bus import EventBus, Event, EventType
from core.controller import Controller
from core.scheduler import Scheduler, PeriodicTask
from services.vision_service import VisionService
from services.voice_service import VoiceService
from services.llm_service import LLMService
from robotics.navigation import Navigator
from robotics.distance_sensor import DistanceSensor
from skills.system_commands import VolumeSkill, OpenApplicationSkill, SystemInfoSkill
from skills.automation import TimerSkill, ListFilesSkill, RunCommandSkill


def setup_logging() -> None:
    """Configure root logger."""
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


async def main() -> None:
    setup_logging()
    logger = logging.getLogger("aura.main")
    logger.info("=" * 50)
    logger.info("  Aura AI System — Starting up")
    logger.info("=" * 50)

    # ── Event bus ─────────────────────────────────────────────────────────────
    bus = EventBus()

    # ── Skills ────────────────────────────────────────────────────────────────
    all_skills = [
        VolumeSkill(bus),
        OpenApplicationSkill(bus),
        SystemInfoSkill(bus),
        TimerSkill(bus),
        ListFilesSkill(bus),
        RunCommandSkill(bus),
    ]

    # ── Controller (receives skills so it can dispatch them) ──────────────────
    controller = Controller(bus, skills=all_skills)

    # ── Robotics ──────────────────────────────────────────────────────────────
    navigator = Navigator(bus)
    navigator.connect()

    # ── Services ──────────────────────────────────────────────────────────────
    loop = asyncio.get_running_loop()

    vision_service = VisionService(bus)
    vision_service.start(loop)

    voice_service = VoiceService(bus)
    voice_service.start(loop)

    # Pass vision_service so LLMService can auto-capture frames
    llm_service = LLMService(bus, vision_service=vision_service)

    services = [controller, navigator, vision_service, voice_service, llm_service]
    logger.info("Services loaded: %d | Skills registered: %d", len(services), len(all_skills))

    # ── Distance sensor — polls at ~10 Hz and publishes DISTANCE_UPDATE ─────────
    distance_sensor = DistanceSensor()

    async def poll_distance():
        distances = distance_sensor.get_distances()
        await bus.publish(Event(EventType.DISTANCE_UPDATE, distances, source="distance_sensor"))

    # ── Scheduler ────────────────────────────────────────────────────────────────
    scheduler = Scheduler()

    async def health_ping():
        logger.debug("System heartbeat — all services running.")

    scheduler.add(PeriodicTask("heartbeat", health_ping, interval_seconds=30))
    scheduler.add(PeriodicTask("distance_poll", poll_distance, interval_seconds=0.1))

    # ── API server (optional) ─────────────────────────────────────────────────
    tasks: list[asyncio.Task] = []

    tasks.append(asyncio.create_task(bus.run(), name="event-bus"))
    tasks.append(asyncio.create_task(scheduler.run(), name="scheduler"))

    if settings.api_enabled:
        from api.api_server import run_server
        tasks.append(asyncio.create_task(run_server(bus), name="api-server"))

    # ── Signal handler for clean shutdown ─────────────────────────────────────
    shutdown_event = asyncio.Event()

    def _on_signal():
        logger.info("Shutdown signal received.")
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, _on_signal)
        except NotImplementedError:
            pass  # Windows doesn't support add_signal_handler for all signals

    # ── Announce ready ────────────────────────────────────────────────────────
    await bus.publish(Event(EventType.SYSTEM_READY, {}, source="main"))
    logger.info("Aura is ready. Say '%s' to activate.", settings.wake_word)

    # ── Run until shutdown ────────────────────────────────────────────────────
    try:
        await shutdown_event.wait()
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    finally:
        logger.info("Shutting down...")
        await bus.publish(Event(EventType.SYSTEM_SHUTDOWN, {}, source="main"))

        voice_service.stop()
        vision_service.stop()
        navigator.disconnect()
        bus.stop()
        scheduler.stop()

        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)

        logger.info("Aura stopped. Goodbye.")


if __name__ == "__main__":
    asyncio.run(main())
