# Aura AI System

An AI-powered robot assistant combining voice control, computer vision, person tracking, and RC car movement — all driven by Google Gemini.

---

## What It Can Do

| Capability | How to trigger |
|---|---|
| **Chat** | Just speak naturally — "What's the weather like?" |
| **Vision / describe scene** | "What do you see?" / "What am I holding?" |
| **Take a photo** | "Take a photo" / "Capture" |
| **Object detection** | Automatic — publishes when objects appear in frame |
| **Face detection** | Automatic — publishes when faces appear in frame |
| **Gesture control** | Open palm → stop car · Thumbs up → acknowledgement |
| **Person follow** | "Follow me" → car tracks and follows you autonomously |
| **Stop following** | "Stop following" / "Cancel follow" |
| **Move the car** | "Move forward" / "Turn left" / "Go back slowly" |
| **Stop** | "Stop" / "Halt" |
| **System info** | "What's the CPU usage?" |
| **Volume** | "Volume up" / "Volume down" / "Mute" |
| **Open apps** | "Open Notepad" |
| **Timer** | "Set a timer for 30 seconds" |
| **List files** | "List files" |

---

## Project Structure

```
MAJOR PROJECT/
├── main.py                     # Entry point
├── .env                        # Your configuration (copy from .env.example)
├── requirements.txt
│
├── ai/                         # LLM layer
│   ├── ai_engine.py            # Orchestrates Gemini calls + memory
│   ├── gemini_client.py        # Raw Gemini API client
│   ├── conversation_memory.py  # Rolling 10-turn chat history
│   ├── prompt_manager.py       # Prompt templates
│   ├── schemas.py              # JSON response schemas
│   └── llm_interface.py        # Abstract base
│
├── audio/                      # Voice pipeline
│   ├── wake_word.py            # Always-on VAD listener (no wake word needed)
│   ├── speech_to_text.py       # faster-whisper STT
│   └── text_to_speech.py       # edge-tts + pygame (offline: pyttsx3)
│
├── vision/                     # Computer vision
│   ├── object_detection.py     # YOLOv8 object detection
│   ├── face_recognition.py     # OpenCV Haar cascade face detection
│   ├── gesture_detection.py    # MediaPipe hand landmarker
│   └── person_tracker.py       # Person position tracker for follow mode
│
├── services/                   # Async service wrappers
│   ├── vision_service.py       # Camera loop + detection at 5 fps
│   ├── voice_service.py        # VAD → STT → event bus
│   └── llm_service.py          # Speech → intent → Gemini
│
├── robotics/                   # RC car control
│   ├── motor_control.py        # Simulation / Serial / HTTP modes
│   ├── navigation.py           # High-level movement + follow loop
│   └── distance_sensor.py      # Front/back ultrasonic (dummy or real)
│
├── core/                       # System backbone
│   ├── event_bus.py            # Async pub/sub message bus
│   ├── controller.py           # Intent router → skills / motors / TTS
│   └── scheduler.py            # Periodic task runner
│
├── skills/                     # Executable skill plugins
│   ├── base_skill.py
│   ├── system_commands.py      # Volume, open app, system info
│   └── automation.py           # Timer, list files, run command
│
├── api/
│   └── api_server.py           # FastAPI REST + WebSocket server
│
├── config/
│   └── settings.py             # Pydantic settings (reads .env)
│
└── utils/
    └── intent_engine.py        # Local rapidfuzz intent fallback
```

---

## Requirements

- **Python 3.11+**
- **Google Gemini API key** — get one free at [aistudio.google.com](https://aistudio.google.com)
- **Microphone** for voice input
- **Webcam** (optional — for vision features)
- **Windows 10/11** (pycaw volume control is Windows-only; other features are cross-platform)

---

## Setup

### 1. Clone / download the project

```bash
cd "d:/WORK SELF/MAJOR PROJECT"
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

### 3. Activate it

```bash
# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

> First install takes ~5–10 minutes (PyTorch, ultralytics, mediapipe are large).

### 5. Configure your API key

Copy `.env.example` to `.env` (or edit `.env` directly):

```bash
copy .env.example .env
```

Open `.env` and set your Gemini key:

```env
GEMINI_API_KEY=your_key_here
```

### 6. Run

```bash
.venv\Scripts\python.exe main.py
```

On first run, the system will automatically download:
- `yolov8n.pt` — YOLO object detection model (~6 MB)
- `vision/hand_landmarker.task` — MediaPipe hand model (~8 MB)
- Whisper `base` model — downloaded by faster-whisper on first use (~140 MB)

---

## Configuration Reference

All settings live in `.env`. Every value has a sensible default.

### LLM

```env
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=models/gemini-2.5-flash   # or gemini-1.5-pro etc.
LLM_TEMPERATURE=0.2                    # 0.0 = deterministic, 1.0 = creative
LLM_MAX_RETRIES=2
```

### Vision / Camera

```env
CAMERA_INDEX=0                         # Local webcam index (0 = default)
RC_VIDEO_URL=                          # RC car stream URL — overrides CAMERA_INDEX
                                       # e.g. http://192.168.4.1:81/stream (MJPEG)
                                       # or   rtsp://192.168.1.100:554/stream
YOLO_MODEL_PATH=yolov8n.pt             # yolov8n (fast) | yolov8s | yolov8m (accurate)
VISION_CONFIDENCE_THRESHOLD=0.5
```

### Audio / Speech-to-Text

```env
WHISPER_MODEL_SIZE=base                # tiny (fast) | base | small | medium | large
WHISPER_DEVICE=cpu                     # cpu | cuda (requires CUDA GPU)
WHISPER_COMPUTE_TYPE=int8              # int8 (fast CPU) | float16 (GPU)
AUDIO_SAMPLE_RATE=16000
```

### Text-to-Speech

```env
TTS_VOICE=en-US-AriaNeural            # Any edge-tts voice
TTS_RATE=+0%                          # Speed: +20% faster, -20% slower
TTS_OFFLINE_FALLBACK=false            # true = use pyttsx3 (no internet needed)
```

Available edge-tts voices: run `edge-tts --list-voices` in terminal.

### RC Car Control

```env
# Control mode
RC_CONTROL_TYPE=simulation            # simulation | serial | http

# Serial mode (Arduino / RPi Pico)
SERIAL_PORT=COM3                      # Windows: COM3, Linux: /dev/ttyUSB0
SERIAL_BAUD_RATE=115200

# HTTP mode (ESP8266 / ESP32 WiFi module)
RC_CONTROL_URL=http://192.168.4.1    # Base URL of your WiFi module
```

**HTTP endpoints expected on the RC car:**
```
GET /forward?speed=0.8
GET /backward?speed=0.8
GET /left?speed=0.8
GET /right?speed=0.8
GET /stop
GET /sensor   → responds with {"front": <cm>, "back": <cm>}
```

**Serial protocol (JSON per line):**
```json
{"command": "move", "direction": "forward", "speed": 0.8}
{"command": "stop"}
```

### Distance Sensor

```env
DUMMY_SENSOR_DATA=true                # true = simulate; false = read from RC HTTP /sensor
OBSTACLE_STOP_DISTANCE=20.0           # Emergency stop if front obstacle closer than X cm
FOLLOW_DISTANCE_MIN=50.0              # Follow mode: move forward if person farther than X cm
FOLLOW_DISTANCE_MAX=100.0             # Follow mode: move backward if person closer than X cm
```

### Person Tracking (Follow Mode)

```env
TRACKING_CENTER_DEADZONE=0.12         # ±12% of frame width = "centred" (no turn command)
TRACKING_AREA_TOO_FAR=0.04            # Person bbox < 4% of frame → move forward
TRACKING_AREA_TOO_CLOSE=0.30          # Person bbox > 30% of frame → move backward
```

### API Server

```env
API_ENABLED=true
API_HOST=0.0.0.0
API_PORT=8000
```

### Logging

```env
LOG_LEVEL=INFO                        # DEBUG | INFO | WARNING | ERROR
```

---

## Voice Commands Reference

The system always listens — no wake word required. Just speak.

### Movement

| Say | Action |
|---|---|
| "Move forward" | Drives forward 1 second at 70% speed |
| "Go back" | Drives backward |
| "Turn left" / "Turn right" | Turns |
| "Move forward fast for 3 seconds" | Speed + duration extracted |
| "Stop" / "Halt" | Immediate stop |

### Follow Mode

| Say | Action |
|---|---|
| "Follow me" | Activates tracking — car follows the largest person in view |
| "Start following" | Same |
| "Stop following" | Deactivates follow mode |
| "Cancel follow" | Same |

### Vision

| Say | Action |
|---|---|
| "What do you see?" | Captures frame → Gemini describes it |
| "What am I holding?" | Same — auto-vision trigger |
| "Describe the scene" | Same |
| "Take a photo" | Saves frame to `captured_images/` |

### Skills

| Say | Action |
|---|---|
| "Volume up / down / mute" | Windows volume control |
| "What's the system info?" | CPU, RAM, disk usage |
| "Open Notepad" | Opens application |
| "Set a timer for 30 seconds" | Countdown timer |
| "List files" | Lists current directory |

### Gesture Control (hands in front of camera)

| Gesture | Action |
|---|---|
| Open palm | Stop the car |
| Thumbs up | Acknowledgement response |

---

## API Reference

While the system is running, the REST API is available at `http://localhost:8000`.

### Health check
```bash
GET /health
```
```json
{"status": "ok", "version": "1.0"}
```

### Text chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "What can you do?"}'
```

### Vision chat (send an image)
```bash
curl -X POST http://localhost:8000/vision \
  -F "file=@photo.jpg" \
  -F "question=What is in this image?"
```

### WebSocket (live bidirectional)
Connect to `ws://localhost:8000/ws` and send JSON:
```json
{"text": "Move forward"}
```
The server broadcasts responses back to all connected clients.

---

## Switching to Real RC Car Hardware

Only `.env` changes are needed — no code modifications.

### Step 1 — WiFi module (ESP8266/ESP32)

```env
RC_CONTROL_TYPE=http
RC_CONTROL_URL=http://192.168.4.1    # your module's IP
RC_VIDEO_URL=http://192.168.4.1:81/stream  # ESP32-CAM stream
```

### Step 2 — Real distance sensor

```env
DUMMY_SENSOR_DATA=false              # reads GET /sensor from RC car
```

### Step 3 — Tune follow behaviour

```env
OBSTACLE_STOP_DISTANCE=25.0          # increase if car stops too early
FOLLOW_DISTANCE_MIN=60.0             # desired following distance (near)
FOLLOW_DISTANCE_MAX=120.0            # desired following distance (far)
TRACKING_CENTER_DEADZONE=0.10        # lower = more responsive turning
```

### Serial (Arduino) instead of WiFi

```env
RC_CONTROL_TYPE=serial
SERIAL_PORT=COM4                     # check Device Manager for correct port
SERIAL_BAUD_RATE=115200
```

Your Arduino sketch should read JSON lines from Serial and drive motors accordingly.

---

## Troubleshooting

### Mic not picking up voice
- Check Windows microphone permissions
- Try increasing VAD sensitivity: edit `_SPEECH_THRESHOLD = 0.01` in [audio/wake_word.py](audio/wake_word.py) — lower value = more sensitive
- Check your default recording device in Windows Sound settings

### TTS not speaking
- Requires internet for edge-tts (Microsoft Azure voices)
- Set `TTS_OFFLINE_FALLBACK=true` to use pyttsx3 offline fallback

### Camera not opening
- Try `CAMERA_INDEX=1` if 0 doesn't work
- For RC stream: ensure you can open the URL in a browser first

### Follow mode not tracking
- Make sure a person is clearly visible in frame
- YOLO must detect label `"person"` — ensure lighting is adequate
- Lower `TRACKING_AREA_TOO_FAR` if car never moves forward (person not detected as big enough)

### Movement commands not working
- Check `RC_CONTROL_TYPE` in `.env` matches your hardware
- In `simulation` mode, commands are only logged — this is expected
- For HTTP mode: test your RC car URL directly in a browser

### Gemini API errors
- Verify `GEMINI_API_KEY` is correct in `.env`
- Check your quota at [aistudio.google.com](https://aistudio.google.com)
- Try `GEMINI_MODEL=models/gemini-1.5-flash` if 2.5-flash is unavailable in your region

---

## Architecture Overview

```
Microphone
    ↓
[VAD Listener]  ──── speech detected
    ↓
[Whisper STT]   ──── text
    ↓
[LLM Service]   ──── SPEECH_TEXT event
    ├── needs_vision? → capture frame → Gemini multimodal
    └── classify intent → Gemini
         ↓
    [Event Bus]
    ├── INTENT_CLASSIFIED → [Controller]
    │       ├── chat/vision → TTS_SPEAK
    │       ├── movement    → MOVEMENT_COMMAND → [Navigator] → [MotorController]
    │       ├── follow      → FOLLOW_MODE → [Navigator] tracking loop
    │       ├── unfollow    → FOLLOW_MODE off
    │       └── skill       → execute → SKILL_DONE → TTS_SPEAK
    │
    ├── [Vision Service] (background thread, 5 fps)
    │       ├── OBJECTS_DETECTED
    │       ├── FACE_DETECTED
    │       ├── GESTURE_DETECTED → [Controller] → stop / ack
    │       └── TRACKING_UPDATE → [Navigator] follow loop
    │
    └── [Distance Sensor] (10 Hz scheduler)
            └── DISTANCE_UPDATE → [Navigator] obstacle safety
```

---

## Adding Custom Skills

Create a class in `skills/` inheriting `BaseSkill`:

```python
from skills.base_skill import BaseSkill
from core.event_bus import EventBus

class MySkill(BaseSkill):
    name = "my_skill"
    description = "Does something cool"
    triggers = ["my_intent", "do_the_thing"]   # LLM intent names that activate this

    async def execute(self, parameters: dict) -> dict:
        # do your thing
        return {"message": "Done!"}   # message is spoken via TTS
```

Register it in `main.py`:
```python
from skills.my_module import MySkill
all_skills = [..., MySkill(bus)]
```

Then add your intent name to the list in `ai/prompt_manager.py` so the LLM knows about it.
