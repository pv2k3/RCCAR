"""
AI Chat & Vision Functions - Usage Examples

This file demonstrates how to use the new chat and vision analysis functions
from the AIEngine class.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.ai_engine import AIEngine


async def example_basic_chat():
    """Example 1: Basic conversational chat."""
    print("\n" + "="*60)
    print("Example 1: Basic Chat")
    print("="*60)
    
    engine = AIEngine()
    
    messages = [
        "Hello! How are you?",
        "What can you help me with?",
        "Tell me an interesting fact about robots.",
    ]
    
    for msg in messages:
        print(f"\n👤 User: {msg}")
        response = await engine.chat(msg)
        print(f"🤖 AI: {response.get('message', response.get('response', 'No response'))}")


async def example_vision_analysis():
    """Example 2: Analyze an image."""
    print("\n" + "="*60)
    print("Example 2: Vision Analysis")
    print("="*60)
    
    engine = AIEngine()
    
    # Make sure you have an image at this path
    image_path = "captured_images/photo_example.jpg"
    
    if not Path(image_path).exists():
        print(f"\n⚠️  Image not found at {image_path}")
        print("📝 To test this, first capture an image using the VisionEngine")
        return
    
    print(f"\n📸 Analyzing image: {image_path}")
    result = await engine.analyze_vision(
        image_path,
        user_query="What objects do you see in this image?"
    )
    
    print("\n📊 Analysis Result:")
    print(f"Description: {result.get('description', 'N/A')}")
    print(f"Objects: {result.get('objects', [])}")
    print(f"Observations: {result.get('observations', [])}")


async def example_vision_chat():
    """Example 3: Chat about an image."""
    print("\n" + "="*60)
    print("Example 3: Vision-Based Chat")
    print("="*60)
    
    engine = AIEngine()
    
    # Make sure you have an image at this path
    image_path = "captured_images/photo_example.jpg"
    
    if not Path(image_path).exists():
        print(f"\n⚠️  Image not found at {image_path}")
        print("📝 To test this, first capture an image using the VisionEngine")
        return
    
    questions = [
        "What's the main focus of this image?",
        "Are there any people in this image?",
        "Describe the lighting and atmosphere.",
    ]
    
    for question in questions:
        print(f"\n👤 User (about image): {question}")
        result = await engine.chat_with_vision(image_path, question)
        print(f"🤖 AI: {result.get('answer', result.get('response', 'No response'))}")


async def example_intent_classification():
    """Example 4: Intent classification."""
    print("\n" + "="*60)
    print("Example 4: Intent Classification")
    print("="*60)
    
    engine = AIEngine()
    
    inputs = [
        "Move forward 10 meters",
        "Hello, how is the weather?",
        "Take a photo",
        "Stop immediately",
    ]
    
    for user_input in inputs:
        print(f"\n👤 Input: {user_input}")
        result = await engine.process(user_input)
        print(f"🎯 Intent: {result.get('intent', 'unknown')}")
        print(f"⚙️  Confidence: {result.get('confidence', 0)}")


async def main():
    """Run all examples."""
    print("\n" + "♦"*60)
    print("♦  AI Engine - Chat & Vision Examples  ♦")
    print("♦"*60)
    
    # Run examples
    await example_basic_chat()
    await example_intent_classification()
    await example_vision_analysis()
    await example_vision_chat()
    
    print("\n" + "="*60)
    print("✅ All examples completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
