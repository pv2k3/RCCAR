"""
Motor control — sends movement commands to the RC car.

Control modes (RC_CONTROL_TYPE in .env):
  simulation  → log-only, no hardware required (default)
  serial      → JSON-per-line over UART to Arduino / RPi Pico
  http        → HTTP GET to an ESP8266/ESP32 WiFi module

HTTP protocol (set RC_CONTROL_URL=http://192.168.4.1):
  GET /forward?speed=0.8
  GET /backward?speed=0.8
  GET /left?speed=0.8
  GET /right?speed=0.8
  GET /stop

Serial protocol (JSON per line):
  {"command": "move", "direction": "forward", "speed": 0.8}
  {"command": "stop"}
"""

import asyncio
import logging
import json

from config.settings import settings

logger = logging.getLogger(__name__)


class MotorController:
    """
    Unified motor controller — simulation, serial, or HTTP.
    Switch modes via RC_CONTROL_TYPE in .env, no code changes needed.
    """

    def __init__(self) -> None:
        self._mode = settings.rc_control_type.lower()
        self._serial = None
        self._port = settings.serial_port
        self._baud = settings.serial_baud_rate
        self._http_url = settings.rc_control_url.rstrip("/")

    def connect(self) -> bool:
        if self._mode == "simulation":
            logger.info("MotorController: simulation mode.")
            return True

        if self._mode == "serial":
            try:
                import serial
                self._serial = serial.Serial(self._port, self._baud, timeout=1)
                logger.info("Serial connected: %s @ %d baud", self._port, self._baud)
                return True
            except Exception as exc:
                logger.error("Serial connection failed: %s — falling back to simulation.", exc)
                self._mode = "simulation"
                return False

        if self._mode == "http":
            logger.info("MotorController: HTTP mode → %s", self._http_url)
            return True

        logger.warning("Unknown RC_CONTROL_TYPE '%s' — using simulation.", self._mode)
        self._mode = "simulation"
        return True

    def disconnect(self) -> None:
        if self._serial and self._serial.is_open:
            self._serial.close()
            logger.info("Serial disconnected.")

    # ── Commands ──────────────────────────────────────────────────────────────

    async def move(self, direction: str, speed: float = 1.0) -> None:
        speed = max(0.0, min(1.0, speed))
        await self._send({"command": "move", "direction": direction, "speed": speed})

    async def stop(self) -> None:
        await self._send({"command": "stop"})

    # ── Transport ─────────────────────────────────────────────────────────────

    async def _send(self, payload: dict) -> None:
        if self._mode == "simulation":
            logger.info("[SIM] Motor: %s", payload)
        elif self._mode == "serial":
            await self._send_serial(payload)
        elif self._mode == "http":
            await self._send_http(payload)

    async def _send_serial(self, payload: dict) -> None:
        if self._serial is None:
            logger.warning("Serial not open — dropping: %s", payload)
            return
        line = json.dumps(payload) + "\n"
        loop = asyncio.get_running_loop()
        try:
            await loop.run_in_executor(None, lambda: self._serial.write(line.encode()))
            logger.debug("Serial → %s", line.strip())
        except Exception as exc:
            logger.error("Serial write failed: %s", exc)

    async def _send_http(self, payload: dict) -> None:
        """
        GET {RC_CONTROL_URL}/{direction}?speed={speed}
        GET {RC_CONTROL_URL}/stop
        """
        loop = asyncio.get_running_loop()
        try:
            import urllib.request
            if payload.get("command") == "stop":
                url = f"{self._http_url}/stop"
            else:
                direction = payload.get("direction", "stop")
                speed = payload.get("speed", 1.0)
                url = f"{self._http_url}/{direction}?speed={speed:.2f}"
            logger.debug("HTTP → %s", url)
            await loop.run_in_executor(None, lambda: urllib.request.urlopen(url, timeout=1).read())
        except Exception as exc:
            logger.warning("HTTP motor command failed: %s", exc)
