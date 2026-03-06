"""
Distance sensor interface.

Modes (controlled by DUMMY_SENSOR_DATA in .env):
  true  → simulated values with realistic drift
  false → reads from RC car HTTP endpoint GET /sensor → {"front": cm, "back": cm}

To switch to real hardware: set DUMMY_SENSOR_DATA=false and ensure
your RC WiFi module exposes GET {RC_CONTROL_URL}/sensor returning JSON.
"""

import logging
import random

from config.settings import settings

logger = logging.getLogger(__name__)


class DistanceSensor:
    """
    Returns front and back ultrasonic distances in centimetres.

    Dummy mode simulates a car parked ~150 cm from obstacles with
    small random drift so the system behaves realistically during testing.
    """

    def __init__(self) -> None:
        self._dummy = settings.dummy_sensor_data
        self._url = settings.rc_control_url
        # Simulated state
        self._sim_front = 150.0
        self._sim_back = 200.0
        logger.info(
            "DistanceSensor initialised (%s mode).",
            "dummy" if self._dummy else "real HTTP",
        )

    def get_distances(self) -> dict:
        """Return {"front": float, "back": float} in cm."""
        if self._dummy:
            return self._simulate()
        return self._read_http()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _simulate(self) -> dict:
        """Drift the simulated readings slightly each call."""
        self._sim_front += random.uniform(-4.0, 4.0)
        self._sim_front = max(5.0, min(400.0, self._sim_front))
        self._sim_back += random.uniform(-4.0, 4.0)
        self._sim_back = max(5.0, min(400.0, self._sim_back))
        return {
            "front": round(self._sim_front, 1),
            "back": round(self._sim_back, 1),
        }

    def _read_http(self) -> dict:
        """
        Read from RC car WiFi module.
        Expected endpoint: GET {RC_CONTROL_URL}/sensor
        Expected response: {"front": <cm>, "back": <cm>}
        """
        try:
            import urllib.request
            import json
            url = f"{self._url}/sensor"
            with urllib.request.urlopen(url, timeout=1) as resp:
                data = json.loads(resp.read().decode())
                return {
                    "front": float(data.get("front", 999.0)),
                    "back": float(data.get("back", 999.0)),
                }
        except Exception as exc:
            logger.warning("Distance sensor HTTP read failed: %s — returning safe defaults", exc)
            return {"front": 999.0, "back": 999.0}
