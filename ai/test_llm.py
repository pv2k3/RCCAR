import asyncio
from ai.gemini_llm import GeminiLLM


async def main():

    llm = GeminiLLM()

    prompt = """
Respond in JSON:
{
  "intent": "",
  "response": "",
  "confidence": 0.0,
  "parameters": {}
}

User: Move forward slowly
"""

    result = await llm.generate(prompt)

    print(result)


if __name__ == "__main__":
    asyncio.run(main())