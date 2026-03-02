"""
Integrated System Test - Combines Speech-to-Text, Intent Detection, and AI Chat/Vision

This test demonstrates the complete workflow:
1. Record audio from microphone
2. Convert speech to text (Whisper)
3. Detect intent using local engine
4. Route to appropriate AI function (Chat, Vision, or Movement)
5. Return structured results

Usage:
    python tests/test_integrated_system.py
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


class IntegratedSystemTest:
    """Complete integrated system test combining all components."""

    def __init__(self):
        print("🔧 Initializing Integrated Test System...\n")
        
        self.stt = SpeechToText(model_size="base", device="cpu", compute_type="int8")
        self.intent_engine = IntentEngine()
        self.ai_engine = AIEngine()
        self.vision_engine = VisionEngine()
        
        print("✅ All components initialized\n")

    # ==========================
    # STEP 1: SPEECH TO TEXT
    # ==========================

    async def record_and_transcribe(self, duration: int = 5) -> str:
        """
        Record audio and convert to text.
        
        Args:
            duration: Recording duration in seconds
            
        Returns:
            Transcribed text
        """
        print(f"\n📢 STEP 1: Speech Recognition")
        print(f"{'='*50}")
        print(f"⏳ Recording for {duration} seconds... (Speak now!)")
        
        start_time = time.time()
        text = await self.stt.listen_and_transcribe(duration=duration)
        elapsed = time.time() - start_time
        
        print(f"✅ Recording complete in {elapsed:.2f}s")
        print(f"📝 Transcribed: \"{text}\"")
        
        return text

    # ==========================
    # STEP 2: INTENT DETECTION
    # ==========================

    def detect_intent(self, text: str) -> dict:
        """
        Detect user intent from text.
        
        Args:
            text: User input text
            
        Returns:
            Intent detection result
        """
        print(f"\n🎯 STEP 2: Intent Detection")
        print(f"{'='*50}")
        
        start_time = time.time()
        result = self.intent_engine.detect_intent(text)
        elapsed = time.time() - start_time
        
        print(f"⚙️  Processing time: {elapsed*1000:.2f}ms")
        print(f"🔍 Detected Intent: {result['intent']}")
        print(f"📊 Confidence: {result['confidence']*100:.1f}%")
        
        return result

    # ==========================
    # STEP 3: CAPTURE IMAGE (IF NEEDED)
    # ==========================

    def capture_reference_image(self) -> str:
        """
        Capture image from camera if vision-related intent.
        
        Returns:
            Path to captured image
        """
        print(f"\n📸 STEP 3: Capturing Reference Image")
        print(f"{'='*50}")
        
        print("🎥 Starting camera...")
        self.vision_engine.start()
        
        print("📸 Capturing photo...")
        time.sleep(1)  # Let camera stream start
        photo_path = self.vision_engine.capture_photo()
        
        self.vision_engine.stop()
        
        if photo_path:
            print(f"✅ Image saved: {photo_path}")
            return photo_path
        else:
            print("❌ Failed to capture image")
            return None

    # ==========================
    # STEP 4: ROUTE & PROCESS
    # ==========================

    async def route_to_ai_function(self, intent: str, text: str, image_path: str = None) -> dict:
        """
        Route to appropriate AI function based on intent.
        
        Args:
            intent: Detected intent
            text: Original user input
            image_path: Optional image path
            
        Returns:
            Processing result
        """
        print(f"\n🤖 STEP 4: AI Processing")
        print(f"{'='*50}")
        
        start_time = time.time()
        result = {}
        
        try:
            if intent == "chat":
                print("💬 Routing to: Chat Mode")
                result = await self.ai_engine.chat(text)
                
            elif intent == "capture_image":
                print("📸 Routing to: Vision Analysis Mode")
                if not image_path:
                    image_path = self.capture_reference_image()
                
                if image_path:
                    result = await self.ai_engine.analyze_vision(image_path)
                else:
                    result = {"error": "Failed to capture image"}
                    
            elif intent == "movement":
                print("🚀 Routing to: Movement Mode")
                movement_params = self.intent_engine.extract_movement_parameters(text)
                print(f"   Direction: {movement_params['direction']}")
                print(f"   Speed: {movement_params['speed']}")
                result = await self.ai_engine.process(text)
                
            elif intent == "stop":
                print("🛑 Routing to: Stop Command")
                result = {
                    "intent": "stop",
                    "action": "halt_all_operations",
                    "status": "executed"
                }
                
            else:
                print("❓ Routing to: Default Intent Processing")
                result = await self.ai_engine.process(text)
            
            elapsed = time.time() - start_time
            print(f"⏱️  Processing time: {elapsed*1000:.2f}ms")
            
            return result
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {"error": str(e)}

    # ==========================
    # COMPLETE WORKFLOW
    # ==========================

    async def run_complete_workflow(self, duration: int = 5, skip_voice: bool = False, 
                                   text_input: str = None, capture_image: bool = False) -> dict:
        """
        Run complete workflow from voice to AI response.
        
        Args:
            duration: Recording duration (seconds)
            skip_voice: Skip voice recording and use text_input instead
            text_input: Manual text input (for testing)
            capture_image: Whether to capture image for vision tasks
            
        Returns:
            Complete workflow result
        """
        workflow_start = time.time()
        
        print("\n" + "🎯"*30)
        print("🎯  INTEGRATED SYSTEM TEST - COMPLETE WORKFLOW  🎯")
        print("🎯"*30 + "\n")
        
        # Step 1: Speech to Text
        if skip_voice:
            text = text_input or "Hello"
            print(f"📝 Using input: \"{text}\"")
        else:
            text = await self.record_and_transcribe(duration=duration)
        
        if not text or len(text.strip()) == 0:
            print("❌ No speech detected. Exiting.")
            return {"error": "No speech input"}
        
        # Step 2: Intent Detection
        intent_result = self.detect_intent(text)
        intent = intent_result["intent"]
        
        # Step 3: Capture Image if needed
        image_path = None
        if (intent == "capture_image" or intent == "vision_analysis") and capture_image:
            image_path = self.capture_reference_image()
        
        # Step 4: Route & Process with AI
        ai_result = await self.route_to_ai_function(intent, text, image_path)
        
        # Final Summary
        total_time = time.time() - workflow_start
        
        print(f"\n{'='*50}")
        print(f"📊 WORKFLOW COMPLETE - Summary")
        print(f"{'='*50}")
        print(f"⏱️  Total time: {total_time:.2f}s")
        print(f"🎙️  Input: \"{text}\"")
        print(f"🎯 Intent: {intent} ({intent_result['confidence']*100:.1f}%)")
        
        # Build comprehensive result
        final_result = {
            "timestamp": time.time(),
            "total_time_seconds": total_time,
            "steps": {
                "speech_to_text": {
                    "input_text": text,
                    "duration_seconds": duration
                },
                "intent_detection": {
                    "intent": intent,
                    "confidence": intent_result['confidence']
                },
                "vision_capture": {
                    "captured": image_path is not None,
                    "image_path": image_path
                },
                "ai_processing": ai_result
            }
        }
        
        print(f"\n✅ Workflow Result:")
        print(json.dumps(final_result, indent=2))
        
        return final_result

    # ==========================
    # QUICK TESTS
    # ==========================

    async def test_chat_only(self, message: str = "Hello! How are you?") -> dict:
        """Quick chat test."""
        print(f"\n{'='*60}")
        print("💬 QUICK TEST: Chat Only")
        print(f"{'='*60}\n")
        
        print(f"Message: \"{message}\"")
        result = await self.ai_engine.chat(message)
        print(f"\nResponse: {json.dumps(result, indent=2)}")
        
        return result

    async def test_vision_analysis(self, image_path: str = None) -> dict:
        """Quick vision analysis test."""
        print(f"\n{'='*60}")
        print("📸 QUICK TEST: Vision Analysis")
        print(f"{'='*60}\n")
        
        if not image_path:
            print("Capturing image from camera...")
            self.vision_engine.start()
            time.sleep(1)
            image_path = self.vision_engine.capture_photo()
            self.vision_engine.stop()
        
        if not image_path:
            print("❌ Failed to capture image")
            return {"error": "No image"}
        
        print(f"Analyzing: {image_path}")
        result = await self.ai_engine.analyze_vision(image_path)
        print(f"\nAnalysis: {json.dumps(result, indent=2)}")
        
        return result

    async def test_vision_chat(self, image_path: str = None, 
                              question: str = "What's in this image?") -> dict:
        """Quick vision chat test."""
        print(f"\n{'='*60}")
        print("🖼️  QUICK TEST: Vision Chat")
        print(f"{'='*60}\n")
        
        if not image_path:
            print("Capturing image from camera...")
            self.vision_engine.start()
            time.sleep(1)
            image_path = self.vision_engine.capture_photo()
            self.vision_engine.stop()
        
        if not image_path:
            print("❌ Failed to capture image")
            return {"error": "No image"}
        
        print(f"Image: {image_path}")
        print(f"Question: {question}")
        result = await self.ai_engine.chat_with_vision(image_path, question)
        print(f"\nResponse: {json.dumps(result, indent=2)}")
        
        return result

    async def test_intent_detection(self, message: str = "Move forward 5 meters") -> dict:
        """Quick intent detection test."""
        print(f"\n{'='*60}")
        print("🎯 QUICK TEST: Intent Detection")
        print(f"{'='*60}\n")
        
        print(f"Input: \"{message}\"")
        result = self.detect_intent(message)
        
        if result["intent"] == "movement":
            params = self.intent_engine.extract_movement_parameters(message)
            print(f"Movement Params: {json.dumps(params, indent=2)}")
        
        return result


# ==========================
# MAIN MENU
# ==========================

async def main():
    """Main menu for testing."""
    test = IntegratedSystemTest()
    
    while True:
        print("\n" + "🎮"*40)
        print("🎮  INTEGRATED SYSTEM TEST MENU  🎮")
        print("🎮"*40)
        print("\n📋 Test Options:")
        print("1. 🎙️  Full Workflow (Voice → Intent → AI)")
        print("2. 💬 Chat Only Test")
        print("3. 📸 Vision Analysis Test")
        print("4. 🖼️  Vision Chat Test")
        print("5. 🎯 Intent Detection Test")
        print("6. 🔄 Workflow with Text Input (No Voice)")
        print("7. ❌ Exit")
        
        choice = input("\nSelect test (1-7): ").strip()
        
        if choice == "1":
            await test.run_complete_workflow(duration=5, capture_image=False)
            
        elif choice == "2":
            await test.test_chat_only()
            
        elif choice == "3":
            await test.test_vision_analysis()
            
        elif choice == "4":
            await test.test_vision_chat()
            
        elif choice == "5":
            await test.test_intent_detection()
            
        elif choice == "6":
            text_input = input("\nEnter text: ").strip()
            if text_input:
                await test.run_complete_workflow(skip_voice=True, text_input=text_input, 
                                               capture_image=True)
            
        elif choice == "7":
            print("\n✅ Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-7.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
