"""
Aura API Server — FastAPI REST + WebSocket interface.

Endpoints:
  GET  /health          — system health check
  POST /chat            — send a text message to the LLM
  POST /vision          — send an image + question to the LLM
  WS   /ws              — real-time bidirectional event stream
"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import settings
from core.event_bus import EventBus, Event, EventType

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections."""

    def __init__(self) -> None:
        self._connections: list[WebSocket] = []

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._connections.append(ws)
        logger.info("WebSocket client connected. Total: %d", len(self._connections))

    def disconnect(self, ws: WebSocket) -> None:
        self._connections.remove(ws)
        logger.info("WebSocket client disconnected. Total: %d", len(self._connections))

    async def broadcast(self, message: dict) -> None:
        """Send a dict as JSON to all connected clients."""
        dead = []
        for ws in self._connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self._connections.remove(ws)


def create_app(bus: EventBus) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        bus: Shared event bus instance.
    """
    manager = ConnectionManager()

    # Forward selected bus events to all WS clients
    async def _forward_event(event: Event) -> None:
        await manager.broadcast({
            "event": event.type.name,
            "payload": event.payload,
            "source": event.source,
        })

    bus.subscribe(EventType.OBJECTS_DETECTED, _forward_event)
    bus.subscribe(EventType.FACE_DETECTED, _forward_event)
    bus.subscribe(EventType.GESTURE_DETECTED, _forward_event)
    bus.subscribe(EventType.SPEECH_TEXT, _forward_event)
    bus.subscribe(EventType.LLM_RESPONSE, _forward_event)
    bus.subscribe(EventType.INTENT_CLASSIFIED, _forward_event)
    bus.subscribe(EventType.MOVEMENT_COMMAND, _forward_event)

    app = FastAPI(title="Aura AI System", version="1.0.0")

    # ── Health ────────────────────────────────────────────────────────────────

    @app.get("/health")
    async def health():
        return {"status": "ok", "system": "aura"}

    # ── Chat ─────────────────────────────────────────────────────────────────

    @app.post("/chat")
    async def chat(body: dict):
        """
        Send a text message to the LLM.

        Body: {"text": "your message"}
        """
        text = body.get("text", "").strip()
        if not text:
            return JSONResponse({"error": "text field required"}, status_code=400)

        await bus.publish(Event(
            EventType.LLM_REQUEST,
            {"text": text},
            source="api",
        ))
        return {"status": "accepted", "text": text}

    # ── Vision + Chat ─────────────────────────────────────────────────────────

    @app.post("/vision")
    async def vision_chat(
        question: str = Form(...),
        image: UploadFile = File(...),
    ):
        """
        Upload an image and ask a question about it.
        """
        import tempfile, os

        contents = await image.read()
        suffix = os.path.splitext(image.filename)[1] or ".jpg"

        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
            f.write(contents)
            tmp_path = f.name

        await bus.publish(Event(
            EventType.LLM_REQUEST,
            {"text": question, "image_path": tmp_path},
            source="api",
        ))
        return {"status": "accepted", "question": question}

    # ── WebSocket ─────────────────────────────────────────────────────────────

    @app.websocket("/ws")
    async def websocket_endpoint(ws: WebSocket):
        await manager.connect(ws)
        try:
            while True:
                data = await ws.receive_json()
                text = data.get("text", "").strip()
                if text:
                    await bus.publish(Event(
                        EventType.LLM_REQUEST,
                        {"text": text},
                        source="websocket",
                    ))
        except WebSocketDisconnect:
            manager.disconnect(ws)

    return app


async def run_server(bus: EventBus) -> None:
    """Start uvicorn server as an asyncio task."""
    app = create_app(bus)
    config = uvicorn.Config(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level=settings.log_level.lower(),
    )
    server = uvicorn.Server(config)
    logger.info("API server starting on %s:%d", settings.api_host, settings.api_port)
    await server.serve()
