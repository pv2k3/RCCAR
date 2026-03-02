import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai.ai_engine import AIEngine


async def main():

    engine = AIEngine()

    print("🤖 Advanced AI Control System (Gemini 2.5 Flash)")
    print("Type 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        try:
            result = await engine.process(user_input)
            print("\nAI Response:")
            print(json.dumps(result, indent=2))
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())