import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.ai_engine import AIEngine


async def chat_mode(engine):
    """Interactive chat mode."""
    print("\n💬 Chat Mode (type 'back' to return to menu)\n")
    
    while True:
        user_message = input("You: ").strip()
        
        if user_message.lower() == "back":
            break
        
        if not user_message:
            continue
        
        try:
            result = await engine.chat(user_message)
            print("\n🤖 AI Response:")
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def vision_chat_mode(engine):
    """Vision-based chat mode."""
    print("\n🖼️ Vision Chat Mode (type 'back' to return to menu)\n")
    
    while True:
        image_path = input("Image path (or 'back'): ").strip()
        
        if image_path.lower() == "back":
            break
        
        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}\n")
            continue
        
        user_message = input("Your question/comment: ").strip()
        
        if not user_message:
            continue
        
        try:
            print("\n🔍 Analyzing image...")
            result = await engine.chat_with_vision(image_path, user_message)
            print("\n🤖 AI Response:")
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def vision_analysis_mode(engine):
    """Vision analysis mode."""
    print("\n📸 Vision Analysis Mode (type 'back' to return to menu)\n")
    
    while True:
        image_path = input("Image path (or 'back'): ").strip()
        
        if image_path.lower() == "back":
            break
        
        if not Path(image_path).exists():
            print(f"❌ Image not found: {image_path}\n")
            continue
        
        custom_query = input("Custom query (optional, press Enter to skip): ").strip()
        
        try:
            print("\n🔍 Analyzing image...")
            result = await engine.analyze_vision(image_path, custom_query)
            print("\n📊 Vision Analysis Result:")
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def intent_mode(engine):
    """Intent classification mode."""
    print("\n🎯 Intent Mode (type 'back' to return to menu)\n")
    
    while True:
        user_input = input("Your input (or 'back'): ").strip()
        
        if user_input.lower() == "back":
            break
        
        if not user_input:
            continue
        
        try:
            result = await engine.process(user_input)
            print("\n🤖 Intent Classification:")
            print(json.dumps(result, indent=2))
            print()
        except Exception as e:
            print(f"❌ Error: {e}\n")


async def main():
    engine = AIEngine()

    print("=" * 60)
    print("🤖 Advanced AI Control System (Gemini 2.5 Flash)")
    print("=" * 60)
    
    while True:
        print("\n📋 Main Menu:")
        print("1. 💬 Chat Mode (conversational AI)")
        print("2. 🖼️  Vision Chat (talk about images)")
        print("3. 📸 Vision Analysis (analyze images)")
        print("4. 🎯 Intent Classification")
        print("5. ❌ Exit")
        
        choice = input("\nSelect mode (1-5): ").strip()
        
        if choice == "1":
            await chat_mode(engine)
        elif choice == "2":
            await vision_chat_mode(engine)
        elif choice == "3":
            await vision_analysis_mode(engine)
        elif choice == "4":
            await intent_mode(engine)
        elif choice == "5":
            print("\n✅ Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")


if __name__ == "__main__":
    asyncio.run(main())