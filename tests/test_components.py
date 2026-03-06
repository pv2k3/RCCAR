"""
Component-level tests for Aura.
Run each test independently to verify individual modules.

Usage:
    python tests/test_components.py
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


# ── Test 1: Speech-to-Text ────────────────────────────────────────────────────

async def test_speech_to_text(duration: int = 5):
    print("\n" + "="*60)
    print("TEST 1: Speech-to-Text (Whisper)")
    print("="*60)

    stt = SpeechToText()
    print(f"Recording {duration}s — speak clearly...")

    t0 = time.time()
    text = await stt.listen_and_transcribe(duration=duration)
    elapsed = time.time() - t0

    print(f"Result ({elapsed:.2f}s): {text!r}")
    return {"status": "ok", "text": text}


# ── Test 2: Intent Detection ──────────────────────────────────────────────────

def test_intent_detection():
    print("\n" + "="*60)
    print("TEST 2: Intent Detection")
    print("="*60)

    engine = IntentEngine()
    samples = [
        "Hello, how are you?",
        "Move forward slowly",
        "Take a picture",
        "Stop right now",
        "Go backward 2 meters",
    ]

    for text in samples:
        result = engine.detect_intent(text)
        print(f"  {text!r}  ->  {result['intent']} ({result['confidence']*100:.0f}%)")
        if result["intent"] == "movement":
            params = engine.extract_movement_parameters(text)
            print(f"    params: {params}")


# ── Test 3: Chat ──────────────────────────────────────────────────────────────

async def test_chat():
    print("\n" + "="*60)
    print("TEST 3: Chat (Gemini)")
    print("="*60)

    engine = AIEngine()
    messages = ["Hello! How are you?", "Tell me about robotics"]

    for msg in messages:
        t0 = time.time()
        response = await engine.chat(msg)
        elapsed = time.time() - t0
        reply = response.get("message") or response.get("response", "")
        print(f"  [{elapsed*1000:.0f}ms] {msg!r}  ->  {str(reply)[:80]}")


# ── Test 4: Vision Analysis ───────────────────────────────────────────────────

async def test_vision_analysis(image_path: str | None = None):
    print("\n" + "="*60)
    print("TEST 4: Vision Analysis (Gemini multimodal)")
    print("="*60)

    if not image_path:
        captured = sorted(Path("captured_images").glob("*.jpg"))
        if captured:
            image_path = str(captured[-1])
        else:
            print("No images in captured_images/. Capture one with the vision service first.")
            return

    print(f"Image: {image_path}")
    engine = AIEngine()
    result = await engine.analyze_vision(image_path, "Describe this image.")
    print(json.dumps(result, indent=2)[:600])


# ── Test 5: Intent Classification via LLM ────────────────────────────────────

async def test_intent_llm():
    print("\n" + "="*60)
    print("TEST 5: Intent Classification (LLM)")
    print("="*60)

    engine = AIEngine()
    samples = ["Turn left 90 degrees", "What's the weather?", "Capture a photo"]

    for text in samples:
        result = await engine.process(text)
        intent = result.get("intent", "?")
        confidence = result.get("confidence", 0)
        print(f"  {text!r}  ->  {intent} ({confidence:.2f})")


# ── Main ──────────────────────────────────────────────────────────────────────

async def main():
    while True:
        print("\n--- Aura Component Tests ---")
        print("1. Speech-to-Text")
        print("2. Intent Detection (local)")
        print("3. Chat (Gemini)")
        print("4. Vision Analysis (Gemini multimodal)")
        print("5. Intent Classification (Gemini)")
        print("6. Exit")
        choice = input("Select (1-6): ").strip()

        if choice == "1":
            await test_speech_to_text()
        elif choice == "2":
            test_intent_detection()
        elif choice == "3":
            await test_chat()
        elif choice == "4":
            await test_vision_analysis()
        elif choice == "5":
            await test_intent_llm()
        elif choice == "6":
            break
        else:
            print("Invalid choice.")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    asyncio.run(main())
