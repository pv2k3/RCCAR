"""
Aura UI — 3D morphing ball visualizer.

Opens a floating window with a 3D-style sphere that deforms in real-time
based on whether the user or Aura is speaking.

States
------
  idle  — slow breathing pulse          (blue)
  user  — spiky burst deformation       (green)  ← user just spoke
  ai    — smooth rolling wave           (purple) ← Aura is speaking

Thread-safe: the visualizer runs its own daemon thread with its own
tkinter mainloop.  External callers communicate only through a
thread-safe queue (no shared widget access).
"""

import math
import queue
import random
import threading
import logging
import tkinter as tk

logger = logging.getLogger(__name__)

_BG_HEX = "#0a0a14"
_BG_RGB = (10, 10, 20)


def _rgb(r: float, g: float, b: float) -> str:
    """Clamp and format (r, g, b) 0-255 floats as a tkinter colour string."""
    return "#{:02x}{:02x}{:02x}".format(
        int(max(0, min(255, r))),
        int(max(0, min(255, g))),
        int(max(0, min(255, b))),
    )


def _lerp_col(a: tuple, b: tuple, t: float) -> tuple:
    """Linear interpolate between two RGB tuples."""
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


class BallVisualizer:
    """
    Floating window showing a 3-D style morphing ball.

    Usage
    -----
        viz = BallVisualizer()
        viz.start()          # launches daemon thread

        viz.set_user_speaking()   # green spiky burst
        viz.set_ai_speaking()     # purple smooth wave
        viz.set_idle()            # blue breathing

        viz.stop()           # closes window & thread
    """

    STATE_IDLE = "idle"
    STATE_USER = "user"
    STATE_AI   = "ai"

    # (base colour, glow/bright colour) per state
    _PALETTE: dict[str, tuple] = {
        STATE_IDLE: ((45,  95, 210), (80,  155, 255)),
        STATE_USER: ((25, 175,  95), (55,  255, 135)),
        STATE_AI:   ((175, 55, 240), (215, 105, 255)),
    }

    # Number of deformation harmonics
    _N_HARM = 14

    def __init__(self, width: int = 390, height: int = 430) -> None:
        self._w = width
        self._h = height

        self._state       = self.STATE_IDLE
        self._amplitude   = 0.02   # current smoothed amplitude
        self._target_amp  = 0.02   # target amplitude

        self._phase = 0.0          # global animation phase

        # Per-harmonic phases and speeds (randomised once)
        self._h_phases = [random.uniform(0.0, 2 * math.pi) for _ in range(self._N_HARM)]
        self._h_speeds = [random.uniform(0.7, 2.8)          for _ in range(self._N_HARM)]

        self._cmd_q: queue.SimpleQueue = queue.SimpleQueue()
        self._root:   tk.Tk     | None = None
        self._canvas: tk.Canvas | None = None

    # ── Public API (thread-safe) ──────────────────────────────────────────────

    def start(self) -> None:
        """Launch the visualizer in a background daemon thread."""
        t = threading.Thread(target=self._run, daemon=True, name="ball-visualizer")
        t.start()
        logger.info("BallVisualizer started.")

    def stop(self) -> None:
        """Signal the visualizer to close."""
        self._cmd_q.put(("quit", None))

    def set_user_speaking(self) -> None:
        """Animate as user-speaking state."""
        self._cmd_q.put(("state", (self.STATE_USER, 0.90)))

    def set_ai_speaking(self) -> None:
        """Animate as AI-speaking state."""
        self._cmd_q.put(("state", (self.STATE_AI, 0.82)))

    def set_idle(self) -> None:
        """Return to idle breathing state."""
        self._cmd_q.put(("state", (self.STATE_IDLE, 0.02)))

    # ── Threading internals ───────────────────────────────────────────────────

    def _run(self) -> None:
        """Entry point for the daemon thread — owns the tkinter mainloop."""
        try:
            self._root = tk.Tk()
            self._root.title("Aura")
            self._root.configure(bg=_BG_HEX)
            self._root.geometry(f"{self._w}x{self._h}+60+60")
            self._root.resizable(False, False)

            self._canvas = tk.Canvas(
                self._root,
                width=self._w,
                height=self._h,
                bg=_BG_HEX,
                highlightthickness=0,
            )
            self._canvas.pack()

            # Start animation loop
            self._root.after(16, self._tick)
            self._root.mainloop()
        except Exception as exc:
            logger.error("BallVisualizer error: %s", exc, exc_info=True)

    def _tick(self) -> None:
        """Animation tick — called every ~16 ms inside the tkinter event loop."""
        # Drain command queue
        while not self._cmd_q.empty():
            try:
                cmd, args = self._cmd_q.get_nowait()
            except Exception:
                break
            if cmd == "quit":
                if self._root:
                    self._root.destroy()
                return
            elif cmd == "state":
                self._state, self._target_amp = args

        # Smooth amplitude towards target
        self._amplitude += (self._target_amp - self._amplitude) * 0.11

        # Gradually decay target amplitude when idle
        if self._state == self.STATE_IDLE:
            self._target_amp = max(0.02, self._target_amp - 0.003)

        # Advance phases
        speed_scale = 1.0 + self._amplitude * 1.5
        self._phase += 0.022 * speed_scale
        for i in range(self._N_HARM):
            self._h_phases[i] += 0.016 * self._h_speeds[i] * speed_scale

        self._draw()

        if self._root:
            self._root.after(16, self._tick)

    # ── Rendering ─────────────────────────────────────────────────────────────

    def _draw(self) -> None:
        c = self._canvas
        c.delete("all")

        cx = self._w // 2
        cy = self._h // 2 - 20      # shift up a bit for the label

        base_r = min(self._w, self._h) * 0.285
        base_col, glow_col = self._PALETTE[self._state]

        # ── 1. Background fill ────────────────────────────────────────────────
        c.create_rectangle(0, 0, self._w, self._h, fill=_BG_HEX, outline="")

        # ── 2. Outer glow rings (concentric ovals interpolated bg→glow) ───────
        n_glow = 10
        for i in range(n_glow, 0, -1):
            t = i / n_glow
            gr = base_r * (1.12 + t * 0.60)
            intensity = t * 0.20 * (0.4 + self._amplitude * 1.4)
            col = _lerp_col(_BG_RGB, glow_col, intensity)
            c.create_oval(cx - gr, cy - gr, cx + gr, cy + gr,
                          fill=_rgb(*col), outline="")

        # ── 3. Deformed ball polygon ──────────────────────────────────────────
        n_pts = 80
        coords: list[float] = []

        for i in range(n_pts):
            angle = 2 * math.pi * i / n_pts

            # Sum harmonics for displacement
            d = 0.0
            for k in range(self._N_HARM):
                freq = k + 1
                # AI: even harmonics dominant (smooth waves)
                # User: all harmonics (spiky random)
                weight = (1.0 / freq) if self._state != self.STATE_AI else (
                    1.0 / freq if freq % 2 == 0 else 0.3 / freq
                )
                d += math.sin(freq * angle + self._h_phases[k]) * weight

            # Normalise and scale by amplitude
            d *= base_r * 0.32 * self._amplitude

            # Idle breathing
            breath = base_r * 0.022 * math.sin(self._phase * 1.4 + angle * 0.3)
            r = base_r + d + breath
            r = max(r, base_r * 0.35)

            coords.append(cx + r * math.cos(angle))
            coords.append(cy + r * math.sin(angle))

        if len(coords) >= 4:
            c.create_polygon(
                coords,
                fill=_rgb(*base_col),
                outline=_rgb(*glow_col),
                smooth=True,
                width=2,
            )

        # ── 4. Inner pseudo-3D gradient (fakes spherical shading) ─────────────
        n_layers = 22
        for i in range(n_layers, 0, -1):
            t = i / n_layers
            ir = base_r * t * 0.86
            # Centre-to-edge: white → base colour
            inner_col = _lerp_col((245, 248, 255), base_col, t ** 0.55)
            c.create_oval(cx - ir, cy - ir, cx + ir, cy + ir,
                          fill=_rgb(*inner_col), outline="")

        # ── 5. Specular highlight (top-left spot) ─────────────────────────────
        hl_r  = base_r * 0.17
        hl_ox = base_r * 0.28
        hl_oy = base_r * 0.28
        c.create_oval(
            cx - hl_ox - hl_r, cy - hl_oy - hl_r,
            cx - hl_ox + hl_r, cy - hl_oy + hl_r,
            fill="#dff0ff", outline="",
        )

        # ── 6. Title and status label ─────────────────────────────────────────
        labels = {
            self.STATE_IDLE: "Idle",
            self.STATE_USER: "Listening…",
            self.STATE_AI:   "Speaking…",
        }
        c.create_text(
            cx, 18,
            text="AURA",
            fill=_rgb(*glow_col),
            font=("Courier New", 13, "bold"),
        )
        c.create_text(
            cx, self._h - 18,
            text=labels.get(self._state, ""),
            fill=_rgb(*glow_col),
            font=("Courier New", 11),
        )
