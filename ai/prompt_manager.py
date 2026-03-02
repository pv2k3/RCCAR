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
Classify into:
- chat
- movement
- capture_image
- stop
- vision_analysis
""",

        "movement": """
Extract:
- direction (forward/backward/left/right)
- speed (slow/medium/fast or numeric)
- duration (seconds if mentioned)
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
    def build_prompt(cls, mode: str, task: str, schema: str, user_input: str, image_data: str = "") -> str:

        system_prompt = cls.SYSTEM_PROMPTS.get(mode, "")
        task_prompt = cls.TASK_PROMPTS.get(task, "")

        base_prompt = f"""
{system_prompt}

{task_prompt}

{schema}

User Input:
{user_input}
"""
        
        # If image data is provided, add it to the prompt
        if image_data:
            base_prompt += f"\n\nImage (base64): {image_data}"

        return base_prompt