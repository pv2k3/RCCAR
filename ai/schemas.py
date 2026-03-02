BASE_SCHEMA = """
Respond strictly in valid JSON.

{
  "intent": "",
  "response": "",
  "confidence": 0.0,
  "parameters": {},
  "metadata": {
      "mode": "",
      "reasoning": ""
  }
}
"""


VISION_SCHEMA = """
{
  "intent": "vision_analysis",
  "response": "",
  "confidence": 0.0,
  "parameters": {
      "objects_of_interest": [],
      "action_required": ""
  },
  "metadata": {
      "mode": "vision",
      "reasoning": ""
  }
}
"""