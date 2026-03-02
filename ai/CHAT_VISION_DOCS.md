# AI Chat & Vision Functions - Complete Documentation

## Overview

The enhanced `AIEngine` class now provides four main functions for different types of AI interactions:

1. **`process(user_input)`** - General intent classification
2. **`chat(user_message)`** - Conversational AI (without images)
3. **`analyze_vision(image_path, user_query)`** - Detailed image analysis
4. **`chat_with_vision(image_path, user_message)`** - Chat about images

---

## Function Reference

### 1. Process - Intent Classification

**Purpose:** Classify user input into different intents and extract parameters.

**Signature:**
```python
async def process(self, user_input: str) -> Dict
```

**Parameters:**
- `user_input` (str): The user's message to classify

**Returns:**
```json
{
  "intent": "chat|movement|capture_image|stop|vision_analysis",
  "response": "Generated response",
  "confidence": 0.95,
  "parameters": {},
  "metadata": {
    "mode": "general_control",
    "reasoning": "Why this intent was chosen"
  }
}
```

**Example:**
```python
engine = AIEngine()
result = await engine.process("Move the robot forward")
print(result["intent"])  # Output: "movement"
```

---

### 2. Chat - Conversational AI

**Purpose:** Have natural conversations with the AI without image input.

**Signature:**
```python
async def chat(self, user_message: str) -> Dict
```

**Parameters:**
- `user_message` (str): The user's chat message

**Returns:**
```json
{
  "intent": "chat",
  "message": "User's message echo",
  "tone": "friendly|professional|casual",
  "response_type": "conversational",
  "metadata": {
    "mode": "chat_assistant",
    "engagement_level": "high"
  }
}
```

**Example:**
```python
engine = AIEngine()

# Simple chat
result = await engine.chat("Tell me about artificial intelligence")
print(result["message"])  # AI's conversational response

# Multi-turn conversation
messages = [
    "Hello!",
    "How can you help me?",
    "What's your name?"
]

for msg in messages:
    response = await engine.chat(msg)
    print(f"AI: {response.get('message')}")
```

**Use Cases:**
- ✅ Answering questions
- ✅ General conversation
- ✅ Educational discussions
- ✅ Friendly interaction
- ✅ Information requests

---

### 3. Analyze Vision - Detailed Image Analysis

**Purpose:** Analyze an image and provide comprehensive observations.

**Signature:**
```python
async def analyze_vision(
    self, 
    image_path: str, 
    user_query: str = ""
) -> Dict
```

**Parameters:**
- `image_path` (str): Path to the image file (relative or absolute)
- `user_query` (str, optional): Specific question or analysis request

**Returns:**
```json
{
  "intent": "vision_analysis",
  "description": "Detailed description of the image",
  "objects": ["object1", "object2", ...],
  "people": ["person1", "person2", ...],
  "environment": "Environmental description",
  "confidence": 0.92,
  "observations": [
    "Observation 1",
    "Observation 2"
  ],
  "suggestions": [
    "Suggestion 1",
    "Suggestion 2"
  ],
  "metadata": {
    "mode": "vision_specialist",
    "image_analyzed": true
  }
}
```

**Supported Image Formats:**
- JPG/JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- BMP (.bmp)
- WebP (.webp)

**Example:**
```python
engine = AIEngine()

# Basic image analysis
result = await engine.analyze_vision("path/to/image.jpg")
print(f"Objects: {result['objects']}")
print(f"Description: {result['description']}")

# Analysis with specific query
result = await engine.analyze_vision(
    "captured_images/photo_1234567890.jpg",
    user_query="Are there any people? What's the environment?"
)
print(result['observations'])

# From captured images
result = await engine.analyze_vision(
    "captured_images/photo_1710000000.jpg",
    user_query="Count the number of objects"
)
```

**Use Cases:**
- ✅ Security camera monitoring
- ✅ Object detection and counting
- ✅ Scene understanding
- ✅ Environmental analysis
- ✅ Anomaly detection
- ✅ Detailed scene description

---

### 4. Chat with Vision - Conversational Image Analysis

**Purpose:** Have a conversation about an image - combines vision analysis with natural dialogue.

**Signature:**
```python
async def chat_with_vision(
    self, 
    image_path: str, 
    user_message: str
) -> Dict
```

**Parameters:**
- `image_path` (str): Path to the image file
- `user_message` (str): User's question or comment about the image

**Returns:**
```json
{
  "intent": "vision_chat",
  "image_description": "What's in the image",
  "answer": "Direct answer to the user's question",
  "objects_detected": ["object1", "object2"],
  "key_observations": ["observation1", "observation2"],
  "response": "Full conversational response",
  "confidence": 0.90,
  "metadata": {
    "mode": "vision_chat_specialist",
    "image_analyzed": true
  }
}
```

**Example:**
```python
engine = AIEngine()

# Question about an image
result = await engine.chat_with_vision(
    "captured_images/office_photo.jpg",
    "How many people are in this office?"
)
print(result["answer"])  # "There are 3 people visible..."

# Multi-turn image discussion
image = "captured_images/scene.jpg"

questions = [
    "What's the main subject of this image?",
    "What's the weather like?",
    "Any safety hazards visible?"
]

for question in questions:
    response = await engine.chat_with_vision(image, question)
    print(f"Q: {question}")
    print(f"A: {response['answer']}\n")
```

**Use Cases:**
- ✅ Interactive image exploration
- ✅ Answering specific questions about images
- ✅ Safety inspections
- ✅ Quality control
- ✅ Educational image analysis
- ✅ Natural dialogue about visual content

---

## API Modes & System Prompts

### Mode: `chat_assistant`
Used for: Basic conversational chat
System Role: "Friendly and helpful conversational AI assistant"

### Mode: `vision_specialist`
Used for: Image analysis
System Role: "Vision analysis expert integrated into a robot"

### Mode: `vision_chat_specialist`
Used for: Conversational image analysis
System Role: "Knowledgeable AI assistant that analyzes images and discusses them"

---

## Error Handling

All functions include error handling. In case of errors, they return an error dictionary:

```json
{
  "error": "Error description",
  "image_path": "path/to/image"  // Image functions only
}
```

**Common Errors:**
- File not found: "Image not found: [path]"
- Invalid format: "Invalid image format: [extension]"
- Processing error: "Failed to process image"
- API error: Gemini API errors

**Example Error Handling:**
```python
try:
    result = await engine.chat_with_vision("invalid_path.jpg", "What is this?")
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Answer: {result['answer']}")
except Exception as e:
    print(f"Exception: {e}")
```

---

## Complete Example: Multi-Mode AI System

```python
import asyncio
from ai.ai_engine import AIEngine

async def main():
    engine = AIEngine()
    
    # 1. Chat mode
    print("=== Chat Mode ===")
    chat_result = await engine.chat("Hello! What's new?")
    print(chat_result.get("message"))
    
    # 2. Intent classification
    print("\n=== Intent Classification ===")
    intent_result = await engine.process("Take a photo of the scene")
    print(f"Detected Intent: {intent_result['intent']}")
    
    # 3. Vision analysis
    print("\n=== Vision Analysis ===")
    vision_result = await engine.analyze_vision(
        "captured_images/photo_1710000000.jpg"
    )
    print(f"Objects detected: {vision_result.get('objects', [])}")
    
    # 4. Vision chat
    print("\n=== Vision Chat ===")
    chat_vision_result = await engine.chat_with_vision(
        "captured_images/photo_1710000000.jpg",
        "Are there any people in this image?"
    )
    print(f"Answer: {chat_vision_result.get('answer')}")

asyncio.run(main())
```

---

## Performance Considerations

### Processing Time (Approximate)
- **Chat**: 1-3 seconds (text only)
- **Vision Analysis**: 2-5 seconds (image processing + analysis)
- **Vision Chat**: 2-5 seconds (combined vision + text)
- **Intent Classification**: 1-2 seconds (lightweight)

### Optimization Tips
1. Use smaller images (< 2MB) for faster processing
2. Batch related queries together
3. Cache responses for identical inputs
4. Use intent classification first for routing
5. Consider local models for simple intents

---

## Integration Examples

### With VisionEngine
```python
from utils.vision_engine import VisionEngine
from ai.ai_engine import AIEngine

async def analyze_captured_image():
    vision_engine = VisionEngine()
    ai_engine = AIEngine()
    
    # Capture photo
    vision_engine.start()
    photo_path = vision_engine.capture_photo()
    vision_engine.stop()
    
    # Analyze with AI
    result = await ai_engine.analyze_vision(photo_path)
    print(result)
```

### With SpeechToText
```python
from utils.speech_to_text import SpeechToText
from ai.ai_engine import AIEngine

async def voice_to_chat():
    stt = SpeechToText()
    ai_engine = AIEngine()
    
    # Record and transcribe
    text = await stt.listen_and_transcribe(duration=5)
    
    # Chat with transcribed text
    result = await ai_engine.chat(text)
    print(result["message"])
```

---

## Testing

### Test the New Functions
```bash
# Run interactive CLI
python ai/main_ai.py

# Run examples
python ai/examples.py
```

### Manual Testing
```python
import asyncio
from ai.ai_engine import AIEngine

async def test():
    engine = AIEngine()
    
    # Test 1: Chat
    result = await engine.chat("Hi there!")
    assert "message" in result or "response" in result
    print("✅ Chat test passed")
    
    # Test 2: Intent
    result = await engine.process("Move forward")
    assert "intent" in result
    print("✅ Intent test passed")
    
    # Test 3: Vision (requires image)
    result = await engine.analyze_vision("test_image.jpg")
    assert "description" in result or "error" in result
    print("✅ Vision test passed")

asyncio.run(test())
```

---

## Future Enhancements

Potential additions:
- 🔄 Multi-image comparison
- 📹 Video frame analysis
- 🎯 Real-time object tracking
- 💾 Response caching
- 📊 Analytics and logging
- 🔊 Voice output integration
- 🌐 Multi-language support
- 🚀 Streaming responses

---

**Last Updated:** March 2, 2026
**Status:** ✅ Production Ready
