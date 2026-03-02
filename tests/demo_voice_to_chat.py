"""
Voice-to-Chat Demonstration

Simple focused test showing the complete voice-to-chat workflow:
1. Record audio from microphone
2. Convert to text (Speech-to-Text)
3. Detect intent
4. Send to AI Chat
5. Display response

This is a minimal example perfect for understanding the pipline.

Usage:
    python tests/demo_voice_to_chat.py
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
from ai.ai_engine import AIEngine


class VoiceToChatDemo:
    """Simple voice-to-chat demonstration."""

    def __init__(self):
        print("\n🎤 Voice-to-Chat Demo - Initialization")
        print("=" * 60)
        
        print("\n🔧 Loading Speech-to-Text model...")
        self.stt = SpeechToText(model_size="base", device="cpu", compute_type="int8")
        print("   ✅ Whisper loaded")
        
        print("🔧 Loading Intent Engine...")
        self.intent_engine = IntentEngine()
        print("   ✅ Intent Engine ready")
        
        print("🔧 Loading AI Engine...")
        self.ai_engine = AIEngine()
        print("   ✅ AI Engine ready")
        
        print("\n✅ All systems ready!\n")

    async def run_demo(self, record_duration: int = 5) -> dict:
        """
        Run the complete voice-to-chat demo.
        
        Args:
            record_duration: How long to record (seconds)
            
        Returns:
            Complete workflow result
        """
        
        print("\n" + "🎯" * 30)
        print("🎯  VOICE-TO-CHAT WORKFLOW DEMO  🎯")
        print("🎯" * 30 + "\n")
        
        # ========== STEP 1: RECORD AUDIO ==========
        print("🎤 STEP 1: Recording Audio")
        print("-" * 60)
        print(f"⏳ Recording for {record_duration} seconds...")
        print("📢 Speak clearly into your microphone!\n")
        
        step1_start = time.time()
        try:
            user_speech = await self.stt.listen_and_transcribe(duration=record_duration)
            step1_time = time.time() - step1_start
        except Exception as e:
            print(f"❌ Recording failed: {e}")
            return {"error": str(e)}
        
        if not user_speech or len(user_speech.strip()) == 0:
            print("❌ No speech detected. Please try again.")
            return {"error": "No speech input"}
        
        print(f"✅ Recording complete ({step1_time:.2f}s)")
        print(f"📝 Transcribed text: \"{user_speech}\"\n")
        
        # ========== STEP 2: DETECT INTENT ==========
        print("🎯 STEP 2: Detecting Intent")
        print("-" * 60)
        
        step2_start = time.time()
        intent_result = self.intent_engine.detect_intent(user_speech)
        step2_time = time.time() - step2_start
        
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        
        print(f"⚙️  Processing time: {step2_time*1000:.2f}ms")
        print(f"🔍 Detected Intent: {intent}")
        print(f"📊 Confidence Score: {confidence*100:.1f}%\n")
        
        # ========== STEP 3: ROUTE TO AI ==========
        print("🤖 STEP 3: Routing to AI")
        print("-" * 60)
        
        if intent != "chat":
            print(f"⚠️  Note: Intent detected as '{intent}' instead of 'chat'")
            print("   Routing to: General AI Processing\n")
        else:
            print("💬 Intent is 'chat' - routing to Chat Function\n")
        
        # ========== STEP 4: GET AI RESPONSE ==========
        print("🤖 STEP 4: Generating AI Response")
        print("-" * 60)
        
        step4_start = time.time()
        try:
            if intent == "chat":
                ai_response = await self.ai_engine.chat(user_speech)
            else:
                ai_response = await self.ai_engine.process(user_speech)
            
            step4_time = time.time() - step4_start
        except Exception as e:
            print(f"❌ AI processing failed: {e}")
            return {"error": str(e)}
        
        print(f"⏱️  AI Processing time: {step4_time*1000:.2f}ms")
        print(f"✅ Response generated\n")
        
        # ========== FINAL RESPONSE ==========
        print("📤 FINAL RESPONSE")
        print("=" * 60)
        
        # Extract message/response
        response_text = ai_response.get('message') or ai_response.get('response') or str(ai_response)
        
        print(f"\n👤 You: \"{user_speech}\"")
        print(f"\n🤖 AI: {response_text}\n")
        
        # ========== SUMMARY ==========
        total_time = time.time() - step1_start
        
        print("=" * 60)
        print("📊 WORKFLOW SUMMARY")
        print("=" * 60)
        print(f"\n⏱️  Total time: {total_time:.2f}s")
        print(f"   ├─ Recording: {step1_time:.2f}s")
        print(f"   ├─ Intent Detection: {step2_time*1000:.2f}ms")
        print(f"   └─ AI Response: {step4_time*1000:.2f}ms")
        
        print(f"\n📊 Details:")
        print(f"   ├─ Speech Input: \"{user_speech}\"")
        print(f"   ├─ Detected Intent: {intent} ({confidence*100:.1f}%)")
        print(f"   └─ AI Response Type: {ai_response.get('response_type', 'standard')}")
        
        # ========== DETAILED JSON RESULT ==========
        print(f"\n📋 Full Result (JSON):")
        print("-" * 60)
        
        result = {
            "timestamp": time.time(),
            "total_time_seconds": total_time,
            "steps": {
                "1_speech_to_text": {
                    "duration_seconds": record_duration,
                    "result_text": user_speech,
                    "processing_time_ms": step1_time * 1000
                },
                "2_intent_detection": {
                    "detected_intent": intent,
                    "confidence": confidence,
                    "processing_time_ms": step2_time * 1000
                },
                "3_ai_chat": {
                    "response": ai_response,
                    "processing_time_ms": step4_time * 1000
                }
            }
        }
        
        print(json.dumps(result, indent=2))
        
        print("\n✅ Demo Complete!\n")
        return result

    async def run_conversation(self, num_turns: int = 3):
        """
        Run a multi-turn conversation.
        
        Args:
            num_turns: Number of conversation turns
        """
        
        print("\n" + "💬" * 30)
        print("💬  MULTI-TURN CONVERSATION DEMO  💬")
        print("💬" * 30 + "\n")
        
        conversation_history = []
        
        for turn in range(num_turns):
            print(f"\n{'='*60}")
            print(f"🗣️  Turn {turn + 1}/{num_turns}")
            print(f"{'='*60}\n")
            
            print(f"⏳ Recording for 5 seconds...")
            print("📢 Speak now!\n")
            
            try:
                user_speech = await self.stt.listen_and_transcribe(duration=5)
                
                if not user_speech:
                    print("❌ No speech detected, skipping turn.\n")
                    continue
                
                print(f"📝 Your: \"{user_speech}\"")
                
                # Get chat response
                ai_response = await self.ai_engine.chat(user_speech)
                response_text = ai_response.get('message', ai_response.get('response', 'No response'))
                
                print(f"🤖 AI: {response_text}\n")
                
                conversation_history.append({
                    "turn": turn + 1,
                    "user": user_speech,
                    "ai": response_text
                })
                
            except Exception as e:
                print(f"❌ Error in turn {turn + 1}: {e}\n")
        
        # Final summary
        print("\n" + "="*60)
        print("📊 CONVERSATION SUMMARY")
        print("="*60 + "\n")
        
        for conv in conversation_history:
            print(f"Turn {conv['turn']}:")
            print(f"  👤 You: \"{conv['user']}\"")
            print(f"  🤖 AI: {conv['ai']}\n")
        
        print("✅ Conversation Complete!\n")
        return conversation_history


# ==========================
# SIMPLE FUNCTIONS
# ==========================

async def quick_demo():
    """Run quick demo without user input."""
    print("\n🎯 Quick Demo (No Voice Required)")
    print("=" * 60)
    
    demo = VoiceToChatDemo()
    
    # Simulate various scenarios
    test_texts = [
        "Hello how are you",
        "Tell me about robotics",
        "What can you do"
    ]
    
    for text in test_texts:
        print(f"\n📝 Simulating: \"{text}\"")
        
        # Detect intent
        intent = demo.intent_engine.detect_intent(text)
        print(f"  → Intent: {intent['intent']} ({intent['confidence']*100:.1f}%)")
        
        # Get chat response
        response = await demo.ai_engine.chat(text)
        chat_response = response.get('message', response.get('response'))
        print(f"  → Response: {chat_response[:80]}...\n")


# ==========================
# MAIN MENU
# ==========================

async def main():
    """Main menu for voice-to-chat demo."""
    
    print("\n" + "🎤" * 40)
    print("🎤  VOICE-TO-CHAT DEMO  🎤")
    print("🎤" * 40)
    
    demo = VoiceToChatDemo()
    
    while True:
        print("\n📋 Menu:")
        print("1. 🎤 Single Voice-to-Chat Demo (5 seconds)")
        print("2. 💬 Multi-turn Conversation (3 turns)")
        print("3. ⚡ Quick Demo (No voice, simulated)")
        print("4. ❌ Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            duration = input("Recording duration (default 5s): ").strip()
            duration = int(duration) if duration.isdigit() else 5
            await demo.run_demo(record_duration=duration)
            
        elif choice == "2":
            turns = input("Number of conversation turns (default 3): ").strip()
            turns = int(turns) if turns.isdigit() else 3
            await demo.run_conversation(num_turns=turns)
            
        elif choice == "3":
            await quick_demo()
            
        elif choice == "4":
            print("\n✅ Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-4.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
