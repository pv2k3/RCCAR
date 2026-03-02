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


CHAT_SCHEMA = """
Respond strictly in valid JSON.

{
  "intent": "chat",
  "message": "",
  "tone": "",
  "response_type": "conversational",
  "metadata": {
      "mode": "chat_assistant",
      "engagement_level": "high"
  }
}
"""


VISION_ANALYSIS_SCHEMA = """
Respond strictly in valid JSON.

{
  "intent": "vision_analysis",
  "description": "",
  "objects": [],
  "people": [],
  "environment": "",
  "confidence": 0.0,
  "observations": [],
  "suggestions": [],
  "metadata": {
      "mode": "vision_specialist",
      "image_analyzed": true
  }
}
"""


VISION_CHAT_SCHEMA = """
Respond strictly in valid JSON.

{
  "intent": "vision_chat",
  "image_description": "",
  "answer": "",
  "objects_detected": [],
  "key_observations": [],
  "response": "",
  "confidence": 0.0,
  "metadata": {
      "mode": "vision_chat_specialist",
      "image_analyzed": true
  }
}
"""