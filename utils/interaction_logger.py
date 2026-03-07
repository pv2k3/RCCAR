"""
Interaction Logger — records every user input and Aura output to disk.

Output files (auto-created under logs/):
  interactions.log   — human-readable timestamped transcript
  interactions.jsonl — one JSON object per line  (easy to parse / analyse)

Call log_user_input() / log_ai_output() from any thread; all writes are
serialised through a threading.Lock to prevent interleaving.
"""

import json
import logging
import os
import threading
from datetime import datetime

logger = logging.getLogger(__name__)


class InteractionLogger:
    """
    Thread-safe file logger for user ↔ Aura interactions.

    Parameters
    ----------
    log_dir : str
        Directory where log files are written.  Created automatically.
    """

    def __init__(self, log_dir: str = "logs") -> None:
        os.makedirs(log_dir, exist_ok=True)
        self._log_path  = os.path.join(log_dir, "interactions.log")
        self._jsonl_path = os.path.join(log_dir, "interactions.jsonl")
        self._lock = threading.Lock()
        logger.info("InteractionLogger: writing to '%s'", log_dir)

    # ── Public API ────────────────────────────────────────────────────────────

    def log_user_input(self, text: str) -> None:
        """Record a user utterance."""
        self._write("USER", text)

    def log_ai_output(self, text: str) -> None:
        """Record an Aura response."""
        self._write("AURA", text)

    # ── Internal ──────────────────────────────────────────────────────────────

    def _write(self, role: str, text: str) -> None:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line  = f"[{ts}] {role}: {text}\n"
        json_obj  = {"ts": ts, "role": role, "text": text}

        with self._lock:
            try:
                with open(self._log_path, "a", encoding="utf-8") as f:
                    f.write(log_line)
                with open(self._jsonl_path, "a", encoding="utf-8") as f:
                    json.dump(json_obj, f, ensure_ascii=False)
                    f.write("\n")
            except OSError as exc:
                logger.error("InteractionLogger write failed: %s", exc)
