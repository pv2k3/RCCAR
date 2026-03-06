"""
Integrated system test — runs the full voice → intent → AI pipeline
without starting the full Aura main loop.

Usage:
    python tests/test_integrated_system.py
"""

import asyncio
import sys
import json
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from audio.speech_to_text import SpeechToText
from utils.intent_engine import IntentEngine
from ai.ai_engine import AIEngine


class IntegratedTest:
    """End-to-end voice → intent → LLM pipeline test."""

    def __init__(self):
        print("Initialising components...")
        self.stt = SpeechToText()
        self.intent = IntentEngine()
        self.ai = AIEngine()
        print("Ready.\n")

    async def run(self, text_input: str | None = None, duration: int = 5) -> dict:
        t_start = time.time()

        # Step 1: Speech or text
        if text_input:
            text = text_input
            print(f"Input: {text!r}")
        else:
            print(f"Recording {duration}s — speak now...")
            text = await self.stt.listen_and_transcribe(duration=duration)
            print(f"Heard: {text!r}")

        if not text.strip():
            return {"error": "No input"}

        # Step 2: Local intent classification
        intent_result = self.intent.detect_intent(text)
        intent = intent_result["intent"]
        confidence = intent_result["confidence"]
        print(f"Intent: {intent} ({confidence*100:.0f}%)")

        # Step 3: LLM processing
        if intent == "chat":
            ai_result = await self.ai.chat(text)
        elif intent == "movement":
            ai_result = await self.ai.process(text)
        else:
            ai_result = await self.ai.process(text)

        reply = ai_result.get("message") or ai_result.get("response", "")
        print(f"AI: {str(reply)[:120]}")

        total = time.time() - t_start
        return {
            "input": text,
            "intent": intent,
            "confidence": confidence,
            "ai_result": ai_result,
            "total_seconds": round(total, 2),
        }


async def main():
    test = IntegratedTest()

    while True:
        print("\n--- Integrated System Test ---")
        print("1. Voice input")
        print("2. Text input")
        print("3. Exit")
        choice = input("Select (1-3): ").strip()

        if choice == "1":
            result = await test.run()
            print("\nFull result:")
            print(json.dumps(result, indent=2, default=str))
        elif choice == "2":
            text = input("Enter text: ").strip()
            if text:
                result = await test.run(text_input=text)
                print("\nFull result:")
                print(json.dumps(result, indent=2, default=str))
        elif choice == "3":
            break
        else:
            print("Invalid choice.")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
