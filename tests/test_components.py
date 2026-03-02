"""
Component-Level Tests

Individual tests for each component:
- Speech-to-Text
- Intent Detection
- Vision Engine
- AI Chat Functions
- Vision Analysis
"""

import asyncio
import sys
import json
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.speech_to_text import SpeechToText
from utils.intent_engine import IntentEngine
from utils.vision_engine import VisionEngine
from ai.ai_engine import AIEngine


# ==========================
# TEST 1: SPEECH-TO-TEXT
# ==========================

async def test_speech_to_text(duration: int = 5, model_size: str = "base"):
    """Test speech-to-text functionality."""
    print("\n" + "="*70)
    print("🎙️  TEST 1: SPEECH-TO-TEXT (Whisper)")
    print("="*70)
    
    try:
        print(f"\n🔧 Initializing SpeechToText with model size: {model_size}")
        stt = SpeechToText(model_size=model_size, device="cpu", compute_type="int8")
        
        print(f"⏳ Recording for {duration} seconds... (Speak clearly!)")
        print("🎤 Recording started...\n")
        
        start_time = time.time()
        text = await stt.listen_and_transcribe(duration=duration)
        elapsed = time.time() - start_time
        
        print("\n" + "-"*70)
        print(f"✅ Transcription complete in {elapsed:.2f}s")
        print(f"📝 Result: \"{text}\"")
        print(f"📊 Length: {len(text)} characters")
        print("-"*70)
        
        return {"status": "success", "text": text, "time_seconds": elapsed}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "error": str(e)}


# ==========================
# TEST 2: INTENT DETECTION
# ==========================

def test_intent_detection(test_inputs: list = None):
    """Test intent detection with various inputs."""
    print("\n" + "="*70)
    print("🎯 TEST 2: INTENT DETECTION")
    print("="*70)
    
    if test_inputs is None:
        test_inputs = [
            "Hello, how are you?",
            "Move forward slowly",
            "Take a picture",
            "Stop right now",
            "What time is it?",
            "Go backward 2 meters"
        ]
    
    try:
        print(f"\n🔧 Initializing IntentEngine")
        engine = IntentEngine()
        
        results = []
        print("\n" + "-"*70)
        
        for i, text in enumerate(test_inputs, 1):
            print(f"\nTest {i}: \"{text}\"")
            
            result = engine.detect_intent(text)
            print(f"  Intent: {result['intent']} (confidence: {result['confidence']*100:.1f}%)")
            
            if result['intent'] == "movement":
                params = engine.extract_movement_parameters(text)
                print(f"  Movement: direction={params['direction']}, speed={params['speed']}")
            
            results.append({
                "input": text,
                "intent": result["intent"],
                "confidence": result["confidence"]
            })
        
        print("\n" + "-"*70)
        print(f"✅ Tested {len(results)} inputs")
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "error": str(e)}


# ==========================
# TEST 3: VISION ENGINE
# ==========================

def test_vision_engine(capture_count: int = 1, show_annotated: bool = True):
    """Test vision engine functionality."""
    print("\n" + "="*70)
    print("📸 TEST 3: VISION ENGINE")
    print("="*70)
    
    try:
        print(f"\n🔧 Initializing VisionEngine")
        vision = VisionEngine()
        
        print(f"🎥 Starting camera stream...")
        vision.start()
        
        # Let camera start
        time.sleep(1)
        
        captured_files = []
        print(f"\n📸 Capturing {capture_count} photo(s)...")
        print("-"*70)
        
        for i in range(capture_count):
            print(f"\n  Photo {i+1}/{capture_count}:")
            
            # Get current frame
            frame = vision.get_frame()
            if frame is not None:
                print(f"    ✅ Frame captured: {frame.shape}")
            else:
                print(f"    ⚠️  Frame not yet available")
            
            # Capture and save
            photo_path = vision.capture_photo()
            if photo_path:
                print(f"    ✅ Saved: {photo_path}")
                captured_files.append(photo_path)
            else:
                print(f"    ❌ Failed to capture")
            
            if i < capture_count - 1:
                time.sleep(0.5)
        
        # Show annotated frame if requested
        if show_annotated:
            print(f"\n🖼️  Generating annotated frame...")
            annotated = vision.annotate_frame()
            if annotated is not None:
                print(f"    ✅ Annotated frame generated: {annotated.shape}")
                print(f"    (Detects: Objects, Hands, Faces)")
            else:
                print(f"    ⚠️  No frame available for annotation")
        
        vision.stop()
        
        print("\n" + "-"*70)
        print(f"✅ Vision test complete")
        print(f"📊 Captured {len(captured_files)} photo(s)")
        
        return {"status": "success", "files": captured_files}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "error": str(e)}


# ==========================
# TEST 4: CHAT FUNCTION
# ==========================

async def test_chat(test_messages: list = None):
    """Test chat functionality."""
    print("\n" + "="*70)
    print("💬 TEST 4: CHAT FUNCTION")
    print("="*70)
    
    if test_messages is None:
        test_messages = [
            "Hello! How are you?",
            "Tell me about robotics",
            "What can you help me with?"
        ]
    
    try:
        print(f"\n🔧 Initializing AIEngine")
        engine = AIEngine()
        
        results = []
        print("\n" + "-"*70)
        
        for i, message in enumerate(test_messages, 1):
            print(f"\nTest {i}:")
            print(f"  You: {message}")
            
            start_time = time.time()
            response = await engine.chat(message)
            elapsed = time.time() - start_time
            
            print(f"  AI: {response.get('message', response.get('response', 'No response'))[:100]}...")
            print(f"  ⏱️  Time: {elapsed*1000:.2f}ms")
            
            results.append({
                "message": message,
                "response": response,
                "time_ms": elapsed*1000
            })
        
        print("\n" + "-"*70)
        print(f"✅ Tested {len(results)} messages")
        
        return {"status": "success", "results": results}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "error": str(e)}


# ==========================
# TEST 5: VISION ANALYSIS
# ==========================

async def test_vision_analysis(image_path: str = None, query: str = None):
    """Test vision analysis functionality."""
    print("\n" + "="*70)
    print("📊 TEST 5: VISION ANALYSIS")
    print("="*70)
    
    if query is None:
        query = "Analyze this image in detail"
    
    try:
        print(f"\n🔧 Initializing AIEngine")
        engine = AIEngine()
        
        # Capture image if not provided
        if not image_path:
            print(f"📸 Capturing image...")
            vision = VisionEngine()
            vision.start()
            time.sleep(1)
            image_path = vision.capture_photo()
            vision.stop()
        
        if not image_path or not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            return {"status": "error", "error": "Image not found"}
        
        print(f"\n📸 Image: {image_path}")
        print(f"❓ Query: {query}")
        print("-"*70)
        
        print(f"\n🔍 Analyzing image...")
        start_time = time.time()
        result = await engine.analyze_vision(image_path, query)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Analysis complete in {elapsed*1000:.2f}ms")
        print(f"\n📊 Result:")
        print(json.dumps(result, indent=2)[:500])
        
        return {"status": "success", "result": result, "time_ms": elapsed*1000}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "error": str(e)}


# ==========================
# TEST 6: VISION CHAT
# ==========================

async def test_vision_chat(image_path: str = None, question: str = None):
    """Test vision chat functionality."""
    print("\n" + "="*70)
    print("🖼️  TEST 6: VISION CHAT")
    print("="*70)
    
    if question is None:
        question = "What's the main focus of this image?"
    
    try:
        print(f"\n🔧 Initializing AIEngine")
        engine = AIEngine()
        
        # Capture image if not provided
        if not image_path:
            print(f"📸 Capturing image...")
            vision = VisionEngine()
            vision.start()
            time.sleep(1)
            image_path = vision.capture_photo()
            vision.stop()
        
        if not image_path or not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}")
            return {"status": "error", "error": "Image not found"}
        
        print(f"\n📸 Image: {image_path}")
        print(f"❓ Question: {question}")
        print("-"*70)
        
        print(f"\n🤖 Processing vision chat...")
        start_time = time.time()
        result = await engine.chat_with_vision(image_path, question)
        elapsed = time.time() - start_time
        
        print(f"\n✅ Chat complete in {elapsed*1000:.2f}ms")
        print(f"\n💬 Response:")
        print(json.dumps(result, indent=2)[:500])
        
        return {"status": "success", "result": result, "time_ms": elapsed*1000}
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"status": "error", "error": str(e)}


# ==========================
# MAIN MENU
# ==========================

async def main():
    """Main menu for component tests."""
    
    while True:
        print("\n" + "🧪"*40)
        print("🧪  COMPONENT-LEVEL TESTS  🧪")
        print("🧪"*40)
        print("\n📋 Available Tests:")
        print("1. 🎙️  Speech-to-Text (Whisper)")
        print("2. 🎯 Intent Detection")
        print("3. 📸 Vision Engine")
        print("4. 💬 Chat Function")
        print("5. 📊 Vision Analysis")
        print("6. 🖼️  Vision Chat")
        print("7. ❌ Exit")
        
        choice = input("\nSelect test (1-7): ").strip()
        
        if choice == "1":
            duration = input("Recording duration (default 5s): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            await test_speech_to_text(duration=duration)
            
        elif choice == "2":
            test_intent_detection()
            
        elif choice == "3":
            test_vision_engine(capture_count=1)
            
        elif choice == "4":
            await test_chat()
            
        elif choice == "5":
            await test_vision_analysis()
            
        elif choice == "6":
            await test_vision_chat()
            
        elif choice == "7":
            print("\n✅ Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-7.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
