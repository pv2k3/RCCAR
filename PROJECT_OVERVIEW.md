# Advanced AI Control System - Project Overview

**Last Updated:** March 2, 2026

## 📋 Project Summary

This is an **Advanced AI-Powered Control System** designed to integrate multiple AI capabilities for multimodal interaction. The system combines computer vision, speech recognition, natural language processing, and large language models (Gemini) to create an intelligent control interface.

---

## 📁 Project Structure

```
WORK SELF/MAJOR PROJECT/
│
├── main.py                    # Entry point (currently empty)
├── yolov8n.pt                 # YOLOv8 Nano model (object detection)
│
├── ai/                         # AI Engine & LLM Integration
│   ├── __pycache__/
│   ├── ai_engine.py           # Main orchestrator for AI processing
│   ├── main_ai.py             # Interactive CLI for AI system
│   ├── gemini_client.py        # Google Gemini API integration
│   ├── llm_interface.py        # Abstract LLM interface
│   ├── prompt_manager.py       # Prompt templates & management
│   └── schemas.py             # JSON schemas for structured responses
│
├── utils/                      # Utility Engines
│   ├── vision_engine.py        # Computer vision pipeline
│   ├── speech_to_text.py       # Audio transcription
│   └── intent_engine.py        # Intent classification & parsing
│
├── captured_images/            # Storage for captured photos
│
├── .venv_cv/                   # Virtual environment (Computer Vision)
├── .venv_llm/                  # Virtual environment (LLM)
├── .env                        # Environment variables (API keys, config)
├── .env.example                # Example env file
├── .git/                       # Git repository
└── .gitignore                  # Git ignore rules
```

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    AIEngine (Orchestrator)                  │
│                                                             │
│  • Processes user input                                    │
│  • Delegates to GeminiClient for intent classification    │
│  • Manages multi-stage reasoning                          │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              Input Processing Layer                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • IntentEngine: Local ML intent classification           │
│  • SpeechToText: Audio → Text (Whisper)                   │
│  • VisionEngine: Multi-modal vision processing            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│              LLM Processing Layer                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  • GeminiClient: Google Generative AI (Gemini 2.5 Flash) │
│  • PromptManager: Dynamic prompt construction            │
│  • LLMInterface: Abstract interface for extensibility    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Core Components

### 1. **AI Engine** (`ai/ai_engine.py`)
- **Purpose:** Main orchestrator for the AI system
- **Key Method:** `async process(user_input: str)`
- **Workflow:**
  1. Takes user input
  2. Builds a prompt using PromptManager
  3. Sends to GeminiClient for processing
  4. Returns structured JSON response
- **Status:** ✅ Implemented

### 2. **Gemini Client** (`ai/gemini_client.py`)
- **Purpose:** Integration with Google Generative AI (Gemini 2.5 Flash)
- **Key Features:**
  - Async API calls via executor
  - Robust JSON parsing with fallback regex extraction
  - Configurable temperature and retry logic
  - Environment variable-based API key management
- **Configuration:**
  - Model: `models/gemini-2.5-flash`
  - Temperature: 0.2 (deterministic outputs)
  - Max Retries: 2
- **Status:** ✅ Implemented

### 3. **Prompt Manager** (`ai/prompt_manager.py`)
- **Purpose:** Centralized prompt template management
- **System Prompts:**
  - `general_control`: Robotics AI controller
  - `movement_specialist`: Motion planning expert
  - `vision_specialist`: Visual analysis expert
  - `chat_assistant`: Conversational assistant
- **Task Prompts:**
  - `intent`: Intent classification
  - `movement`: Movement parameter extraction
  - `vision`: Vision analysis recommendations
- **Status:** ✅ Implemented

### 4. **Schemas** (`ai/schemas.py`)
- **Purpose:** Define JSON response formats
- **Schemas:**
  - `BASE_SCHEMA`: Standard response format with intent, response, confidence, parameters, metadata
  - `VISION_SCHEMA`: Vision-specific response format with objects_of_interest
- **Status:** ✅ Implemented

### 5. **Vision Engine** (`utils/vision_engine.py`)
- **Purpose:** Complete computer vision pipeline
- **Key Features:**
  - Singleton pattern for single instance management
  - **Object Detection:** YOLOv8 Nano model
  - **Hand Detection:** MediaPipe Hands
  - **Face Detection:** MediaPipe Face Detection
  - Real-time frame capture and processing
  - Threaded frame capture for smooth streaming
  - Photo capture with timestamp naming
- **Capabilities:**
  - Live frame access with thread-safe locking
  - Annotated frame generation with all detections overlaid
  - Real-time detection visualization
- **Test Mode:** Interactive CLI with Q (quit) and C (capture) controls
- **Status:** ✅ Fully Implemented

### 6. **Speech-to-Text Engine** (`utils/speech_to_text.py`)
- **Purpose:** Audio transcription using OpenAI Whisper
- **Key Features:**
  - Faster Whisper (CPU-optimized)
  - Configurable model sizes (tiny, base, small, medium, large-v3)
  - Real-time microphone recording
  - Async-compatible interface
  - Int8 quantization for CPU efficiency
- **Methods:**
  - `record_audio(duration, sample_rate)`: Captures audio from microphone
  - `transcribe(audio, sample_rate)`: Converts audio to text
  - `async listen_and_transcribe(duration)`: Async wrapper
- **Status:** ✅ Implemented

### 7. **Intent Engine** (`utils/intent_engine.py`)
- **Purpose:** Local intent classification without LLM overhead
- **Key Features:**
  - Pattern matching with RapidFuzz similarity scoring
  - Configurable confidence threshold (default: 60%)
  - Movement parameter extraction
- **Supported Intents:**
  - `chat`: General conversation
  - `capture_image`: Camera operations
  - `movement`: Robot movement commands
  - `stop`: Halt commands
- **Methods:**
  - `detect_intent(text)`: Returns intent + confidence
  - `extract_movement_parameters(text)`: Extracts direction and speed
- **Status:** ✅ Implemented

### 8. **LLM Interface** (`ai/llm_interface.py`)
- **Purpose:** Abstract base class for LLM implementations
- **Methods:** `async generate(prompt)` (abstract)
- **Design:** Allows future implementations (Claude, GPT, local models)
- **Status:** ✅ Implemented (Abstract)

### 9. **Main AI CLI** (`ai/main_ai.py`)
- **Purpose:** Interactive command-line interface for testing
- **Features:**
  - Multi-turn conversation loop
  - Async/await pattern
  - Error handling with user feedback
  - Clean JSON output formatting
- **Usage:** Type commands, see AI responses
- **Status:** ✅ Implemented

---

## 🎛️ Technologies & Dependencies

### AI & ML Libraries
- **Google Generative AI** (Gemini 2.5 Flash)
- **OpenAI Whisper** (Faster Whisper) - Speech Recognition
- **YOLOv8** (Nano) - Object Detection
- **MediaPipe** - Hand & Face Detection
- **RapidFuzz** - Fuzzy string matching

### Core Libraries
- **AsyncIO** - Asynchronous operations
- **OpenCV (cv2)** - Computer vision processing
- **NumPy** - Numerical operations
- **Python-dotenv** - Environment variable management

### Environment Setup
- **Python Virtual Environments:**
  - `.venv_cv/` - Computer Vision dependencies
  - `.venv_llm/` - LLM dependencies
  - Can be separated or unified

---

## 📊 Current Implementation Status

| Component | Status | Description |
|-----------|--------|-------------|
| AIEngine | ✅ Done | Orchestrates intent classification and LLM processing |
| GeminiClient | ✅ Done | Full integration with Gemini 2.5 Flash API |
| PromptManager | ✅ Done | Flexible prompt templating system |
| Schemas | ✅ Done | JSON response format definitions |
| LLMInterface | ✅ Done | Abstract interface for extensibility |
| VisionEngine | ✅ Done | YOLO + MediaPipe comprehensive vision pipeline |
| SpeechToText | ✅ Done | Whisper-based transcription (CPU-optimized) |
| IntentEngine | ✅ Done | Local ML-based intent classification |
| Main AI CLI | ✅ Done | Interactive testing interface |
| Main Entry Point | ⚠️ Empty | Ready for high-level application integration |

---

## 🚀 Capabilities

### Current Features
1. **Intent Classification**
   - LLM-based (Gemini) and local (RapidFuzz) methods
   - Confidence scoring
   - Support for: chat, movement, image capture, stop commands

2. **Computer Vision**
   - Real-time object detection (YOLO)
   - Hand pose estimation (MediaPipe)
   - Face detection (MediaPipe)
   - Photo capture with timestamps
   - Live annotation and visualization

3. **Speech Processing**
   - Audio transcription (Whisper)
   - Microphone input capture
   - Async processing

4. **LLM Integration**
   - Async API calls
   - Structured JSON responses
   - Configurable generation parameters
   - Retry logic with JSON parsing fallback

---

## 📝 Configuration

### Environment Variables (.env)
```
GEMINI_API_KEY=your_api_key_here
```

### Model Parameters
- **Gemini:**
  - Model: `models/gemini-2.5-flash`
  - Temperature: 0.2 (deterministic)
  - Max Retries: 2

- **Whisper:**
  - Model: `base` (configurable)
  - Device: `cpu`
  - Compute Type: `int8` (quantized for efficiency)

- **YOLO:**
  - Model: `yolov8n.pt` (Nano - lightweight)

---

## 🔄 Workflow Example

```
User Input: "take a photo to the left"
    ↓
IntentEngine: Detects intent = "capture_image" (confidence: 0.85)
    ↓
AIEngine: Builds prompt with movement parameters
    ↓
GeminiClient: Sends to Gemini API
    ↓
Gemini Response (JSON):
{
  "intent": "capture_image",
  "response": "Turning left and capturing image...",
  "confidence": 0.95,
  "parameters": {
    "direction": "left",
    "capture": true
  },
  "metadata": {
    "mode": "general_control",
    "reasoning": "User requested to capture image to the left"
  }
}
    ↓
Application: Execute movement and capture logic
```

---

## 🎯 Next Steps / TODO

1. **Main Entry Point Enhancement**
   - Integrate all components in `main.py`
   - Implement vision + speech + AI pipeline
   - Add movement execution layer

2. **Extended Capabilities**
   - Vision feedback loops (real-time scene understanding)
   - Multi-modal request handling (speech + vision + text)
   - Persistence layer (store interactions/logs)

3. **Performance Optimization**
   - Model quantization for faster inference
   - Caching for repeated queries
   - Batch processing for multiple inputs

4. **Production Readiness**
   - Error handling & logging
   - Rate limiting & quota management
   - Authentication & security hardening
   - Unit & integration tests
   - Documentation & examples

---

## 📞 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp .env.example .env
# Edit .env and add GEMINI_API_KEY
```

### 3. Run Interactive AI CLI
```bash
python ai/main_ai.py
```

### 4. Test Vision Engine
```bash
python utils/vision_engine.py
# Press Q to quit, C to capture
```

### 5. Test Speech-to-Text
```bash
python utils/speech_to_text.py
# Speak for 5 seconds, see transcription
```

---

## 📚 File Reference

| File | Lines | Purpose |
|------|-------|---------|
| `ai/ai_engine.py` | 25 | Main orchestrator |
| `ai/gemini_client.py` | 65 | Gemini API client |
| `ai/prompt_manager.py` | 55 | Prompt templates |
| `ai/schemas.py` | 30 | JSON schemas |
| `ai/llm_interface.py` | 8 | Abstract interface |
| `ai/main_ai.py` | 37 | CLI interface |
| `utils/vision_engine.py` | 207 | Vision pipeline |
| `utils/speech_to_text.py` | 96 | STT engine |
| `utils/intent_engine.py` | 97 | Intent classification |

---

## ✨ Key Strengths

- ✅ **Modular Architecture** - Each component is independent and testable
- ✅ **Async-First Design** - Scalable, non-blocking operations
- ✅ **Multi-Modal** - Integrates vision, speech, and text
- ✅ **Extensible** - Abstract interfaces for future implementations
- ✅ **Error Resilient** - Retry logic, fallback parsing, try-catch handlers
- ✅ **Efficient** - CPU-optimized models, quantization
- ✅ **Real-time** - Threaded vision pipeline, live streaming

---

**Project Status:** 🟢 Core Implementation Complete - Ready for Application Integration
