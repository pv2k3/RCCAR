class PromptManager:

    SYSTEM_PROMPTS = {

        "general_control": """
You are a robotics AI controller.
You classify user intent and extract structured parameters.
""",

        "movement_specialist": """
You are an expert robotics motion planner.
Extract safe movement instructions.
Always prioritize safety.
""",

        "vision_specialist": """
You are a vision analysis expert integrated into a robot.
Analyze images and describe what you see.
Focus on environmental awareness and object detection.
Provide detailed observations and suggestions.
""",

        "chat_assistant": """
You are a friendly and helpful conversational AI assistant integrated into a robot.
Respond in a natural, concise but informative manner.
Be engaging and helpful.
""",

        "vision_chat_specialist": """
You are a knowledgeable AI assistant that can analyze images and have conversations about them.
Describe what you observe in the provided image.
Answer questions about the image content.
Provide insights and suggestions based on visual information.
Be helpful and detailed in your analysis.
"""
    }

    TASK_PROMPTS = {

        "intent": """
Classify the user's message into exactly one of:
- chat            (general conversation, questions, anything else)
- movement        (move, go, drive, turn, forward, backward, left, right)
- capture_image   (take photo, capture, snapshot)
- stop            (stop, halt, freeze, don't move)
- vision_analysis (analyze image, describe picture)
- follow          (follow me, start following, track me, come with me)
- unfollow        (stop following, stop tracking, cancel follow, stay)

For movement, extract parameters: direction (forward/backward/left/right/turn_left/turn_right), speed (0.0-1.0), duration (seconds).
""",

        "movement": """
Extract:
- direction (forward/backward/left/right/turn_left/turn_right)
- speed (slow=0.4 / medium=0.7 / fast=1.0 or numeric 0.0-1.0)
- duration (seconds if mentioned, default 1.0)
""",

        "general_chat": """
Respond naturally to the user's message.
Be helpful, friendly, and informative.
Keep responses concise but useful.
""",

        "vision_analysis": """
Analyze the provided image and describe:
- Objects detected in the scene
- People, animals, or notable features
- Environmental conditions
- Spatial layout and positioning
- Any anomalies or interesting observations
""",

        "vision_chat": """
Analyze the image and respond to the user's question about it.
First describe what you observe in the image.
Then answer the specific question or request.
Provide detailed and accurate information.
"""
    }

    @classmethod
    def build_prompt(
        cls,
        mode: str,
        task: str,
        schema: str,
        user_input: str,
        history: str = "",
    ) -> str:
        system_prompt = cls.SYSTEM_PROMPTS.get(mode, "")
        task_prompt = cls.TASK_PROMPTS.get(task, "")
        history_block = f"\n{history}\n" if history else ""

        return f"""{system_prompt}

{task_prompt}

{schema}
{history_block}
User Input:
{user_input}
"""