# 🧪 Testing Suite - Complete Guide

## Overview

This directory contains comprehensive tests for the AI system, combining:
- ✅ Speech-to-Text (Whisper)
- ✅ Intent Detection
- ✅ Computer Vision (YOLO + MediaPipe)
- ✅ LLM Chat Functions
- ✅ Vision Analysis & Chat

---

## 📁 Test Files

### 1. **test_integrated_system.py** - Complete Workflow
**Purpose:** Tests the entire pipeline end-to-end
- 🎤 Records audio from microphone
- 📝 Converts speech to text
- 🎯 Detects user intent
- 🖼️ Captures images if needed
- 🤖 Routes to appropriate AI function
- 📊 Returns complete result

**Quick Tests Available:**
- Full workflow with voice
- Chat-only test
- Vision analysis test
- Vision chat test
- Intent detection test
- Workflow with text input (no voice)

### 2. **test_components.py** - Individual Component Tests
**Purpose:** Tests each component independently

**Tests:**
1. Speech-to-Text (Whisper)
2. Intent Detection
3. Vision Engine
4. Chat Function
5. Vision Analysis
6. Vision Chat

---

## 🚀 Quick Start

### Prerequisites

1. **Activate Virtual Environment**
```bash
# Windows
.\.venv_cv\Scripts\Activate.ps1

# Mac/Linux
source .venv_cv/bin/activate
```

2. **Ensure Dependencies Installed**
```bash
pip install google-generativeai opencv-python-headless ultralytics mediapipe python-dotenv faster-whisper sounddevice numpy rapidfuzz
```

3. **Set API Key**
```bash
# Create .env file if not exists
cp .env.example .env

# Edit .env and add:
GEMINI_API_KEY=your_api_key_here
```

---

## 🧪 Running Tests

### Option 1: Full Integrated Test (Recommended First)

```bash
python tests/test_integrated_system.py
```

**Menu:**
```
1. 🎙️  Full Workflow (Voice → Intent → AI)
2. 💬 Chat Only Test
3. 📸 Vision Analysis Test
4. 🖼️  Vision Chat Test
5. 🎯 Intent Detection Test
6. 🔄 Workflow with Text Input (No Voice)
7. ❌ Exit
```

**Test 1 - Full Workflow Example:**
```
Select test (1-7): 1
⏳ Recording for 5 seconds... (Speak now!)
👤 User: "Move forward"
🎯 Intent: movement (95% confidence)
🤖 Processing...
✅ Complete
```

### Option 2: Component Tests

```bash
python tests/test_components.py
```

**Menu:**
```
1. 🎙️  Speech-to-Text (Whisper)
2. 🎯 Intent Detection
3. 📸 Vision Engine
4. 💬 Chat Function
5. 📊 Vision Analysis
6. 🖼️  Vision Chat
7. ❌ Exit
```

---

## 📖 Test Scenarios

### Scenario 1: Voice-to-Chat Workflow

**Goal:** Record voice, detect intent, respond with chat

**Steps:**
1. Run: `python tests/test_integrated_system.py`
2. Select: `1` (Full Workflow)
3. Speak: Any conversational message (e.g., "Hello!")
4. Watch system:
   - 🎙️ Transcribe speech
   - 🎯 Detect chat intent
   - 💬 Generate response

**Expected Output:**
```
📢 STEP 1: Speech Recognition
✅ Recording complete
📝 Transcribed: "Hello how are you"

🎯 STEP 2: Intent Detection
🔍 Detected Intent: chat
📊 Confidence: 98%

🤖 STEP 4: AI Processing
💬 Routing to: Chat Mode
✅ Response generated
```

---

### Scenario 2: Voice-to-Vision with Camera

**Goal:** Record voice requesting image, capture photo, analyze

**Steps:**
1. Run: `python tests/test_integrated_system.py`
2. Select: `6` (Text Input)
3. Enter: `"take a photo"`
4. System will:
   - 🎯 Detect intent as "capture_image"
   - 📸 Capture from camera
   - 📊 Analyze with AI

**Expected Output:**
```
🎯 STEP 2: Intent Detection
🔍 Detected Intent: capture_image
📸 STEP 3: Capturing Reference Image
✅ Image saved: captured_images/photo_1234567890.jpg

🤖 STEP 4: AI Processing
📸 Routing to: Vision Analysis Mode
✅ Analysis complete
```

---

### Scenario 3: Quick Chat Without Voice

**Goal:** Test chat without microphone/voice

**Steps:**
1. Run: `python tests/test_components.py`
2. Select: `4` (Chat Function)
3. System will test predefined messages

**Expected Output:**
```
Test 1:
  You: "Hello! How are you?"
  AI: "I'm doing well, thank you for asking!..."
  ⏱️  Time: 1234.56ms
```

---

### Scenario 4: Vision Analysis on Captured Image

**Goal:** Capture image from camera, analyze with AI

**Steps:**
1. Run: `python tests/test_integrated_system.py`
2. Select: `3` (Vision Analysis Test)
3. System will:
   - 📸 Capture image from camera
   - 📊 Analyze using Gemini AI
   - 🔍 Return detailed observations

**Expected Output:**
```
📸 Capturing image from camera...
✅ Image saved: captured_images/photo_1234567890.jpg

🔍 Analyzing image...
✅ Analysis complete in 3456.78ms

📊 Result:
{
  "description": "A well-lit indoor office environment...",
  "objects": ["desk", "computer", "chair", "window"],
  "people": [],
  ...
}
```

---

### Scenario 5: Chat About Image

**Goal:** Show AI an image and ask questions about it

**Steps:**
1. Run: `python tests/test_integrated_system.py`
2. Select: `4` (Vision Chat Test)
3. System will:
   - 📸 Capture image
   - 💬 Ask predefined question
   - 🤖 Respond with vision-aware answer

**Expected Output:**
```
🖼️  Vision Chat Test
📸 Image: captured_images/photo_1234567890.jpg
❓ Question: "What's the main focus?"

🤖 Response:
{
  "image_description": "Indoor office scene...",
  "answer": "The main focus appears to be the work desk...",
  "objects_detected": ["desk", "computer"],
  ...
}
```

---

## 🎤 Voice Input Tips

### For Best Results:

1. **Clear Speech**
   - Speak clearly and naturally
   - Avoid background noise
   - Use standard pronunciation

2. **Microphone Quality**
   - Use a decent microphone (laptop mic or external)
   - Position microphone 6-12 inches away
   - Minimize background noise

3. **Recording Duration**
   - Default: 5 seconds
   - Can be adjusted in test menu
   - System waits for full duration

4. **Test Sentences**
   ```
   "Hello how are you"
   "Move forward slowly"
   "Take a photo"
   "Stop the robot"
   "Tell me about this scene"
   ```

---

## 📊 Test Results Interpretation

### Speech-to-Text Results

```json
{
  "status": "success",
  "text": "move forward five meters",
  "time_seconds": 4.23,
  "confidence": 0.92
}
```
- ✅ `"success"` - Audio captured and transcribed
- 📝 `"text"` - Detected speech
- ⏱️ `"time_seconds"` - Processing time
- 📊 `"confidence"` - Accuracy score (rarely shown by Whisper)

### Intent Detection Results

```json
{
  "intent": "movement",
  "confidence": 0.95
}
```
- **Possible Intents:**
  - `chat` - General conversation
  - `movement` - Robot movement
  - `capture_image` - Photo capture
  - `stop` - Stop command
  - `vision_analysis` - Analyze scene

### Chat Response

```json
{
  "intent": "chat",
  "message": "Hello! I'm happy to chat with you...",
  "tone": "friendly",
  "response_type": "conversational"
}
```
- 💬 Natural language response
- 😊 Tone indicator (friendly, professional, casual)
- 📊 Response type (conversational, technical, etc.)

### Vision Analysis Result

```json
{
  "intent": "vision_analysis",
  "description": "A bright office with...",
  "objects": ["desk", "computer", "chair"],
  "observations": ["Well-lit environment", "Organized workspace"],
  "suggestions": ["Good lighting for work"]
}
```
- 📸 Image description
- 🔍 Objects detected
- 💡 Observations made
- 💭 Suggestions provided

---

## 🔧 Troubleshooting

### Issue: "No speech detected"

**Cause:** Microphone not working or too quiet

**Solution:**
```bash
# Test microphone
python -c "import sounddevice as sd; print(sd.query_devices())"

# Use text input instead (Option 6)
python tests/test_integrated_system.py
# Select 6: Workflow with Text Input
```

### Issue: "Image not found"

**Cause:** Camera not available or image capture failed

**Solution:**
```bash
# Test vision engine
python tests/test_components.py
# Select 3: Vision Engine
# Follow the test instructions
```

### Issue: "API Error - Gemini"

**Cause:** Missing or invalid API key

**Solution:**
1. Check `.env` file has `GEMINI_API_KEY`
2. Verify API key is correct
3. Check quota/usage limits

### Issue: "Failed to load model"

**Cause:** Missing dependencies or internet connection needed

**Solution:**
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# For Whisper model download:
python -c "from faster_whisper import WhisperModel; WhisperModel('base')"
```

---

## 📈 Performance Expectations

| Component | Time | Notes |
|-----------|------|-------|
| Speech-to-Text | 4-6s | Depends on duration |
| Intent Detection | 50-200ms | Local ML |
| Image Analysis | 2-5s | Gemini API call |
| Chat Response | 1-3s | Gemini API call |
| Vision Chat | 2-5s | Image + text |
| Vision Engine | 1s+ | Initialization |

---

## 💾 Output Files

### Captured Images
Location: `captured_images/`

Files are named: `photo_TIMESTAMP.jpg`
- Example: `photo_1234567890.jpg`

### Test Logs
Each test prints detailed information to console:
- ✅ Success/failure status
- ⏱️ Timing information
- 📊 Results in JSON format

---

## 🎯 Testing Workflow Recommendation

### Beginner:
1. Start with component tests
2. Test each component individually
3. Build comfort with system

### Intermediate:
1. Run integrated tests with text input
2. Gradually move to voice tests
3. Combine multiple components

### Advanced:
1. Run full voice-to-vision workflows
2. Test edge cases
3. Monitor performance metrics

---

## 🔗 Integration with Main Application

Once tests pass, use in main application:

```python
from tests.test_integrated_system import IntegratedSystemTest

async def main():
    test = IntegratedSystemTest()
    result = await test.run_complete_workflow(duration=5)
    print(result)
```

---

## ✨ Advanced Features

### Custom Test Messages

Edit test files to use custom inputs:

```python
# In test_components.py
test_messages = [
    "Your custom message 1",
    "Your custom message 2"
]

await test_chat(test_messages)
```

### Custom Recording Duration

```bash
# When prompted for duration
Recording duration (default 5s): 10
# Will record for 10 seconds
```

### Batch Testing

```python
# Run multiple tests sequentially
async def batch_test():
    await test_chat()
    await test_vision_analysis()
    await test_vision_chat()
```

---

## 📝 Common Test Commands

```bash
# Run full integrated test
python tests/test_integrated_system.py

# Run component tests
python tests/test_components.py

# Run with Python directly
python -m tests.test_integrated_system

# Run specific component
python -c "from tests.test_components import test_chat; import asyncio; asyncio.run(test_chat())"
```

---

## 🎓 Learning Path

1. **Day 1:** Run component tests individually
2. **Day 2:** Run integrated test with text input
3. **Day 3:** Run integrated test with voice
4. **Day 4:** Combine system with your code

---

## 🆘 Get Help

### If test fails:
1. Check error message carefully
2. Review troubleshooting section
3. Check API key and dependencies
4. Try individual component tests

### Sample Error Messages:
```
❌ Image not found: captured_images/photo_1234567890.jpg
  → Camera need to capture first

❌ API Error - Could not authenticate
  → Check GEMINI_API_KEY in .env

❌ No speech detected
  → Use text input option or check microphone
```

---

## ✅ Checklist - Before Running Tests

- [ ] Virtual environment activated
- [ ] Dependencies installed
- [ ] `.env` file configured with API key
- [ ] Microphone connected (for voice tests)
- [ ] Camera available (for vision tests)
- [ ] Internet connection active
- [ ] YOLOv8n.pt model in project root

---

**Last Updated:** March 2, 2026  
**Version:** 1.0  
**Status:** ✅ Ready to Use
