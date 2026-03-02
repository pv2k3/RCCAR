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
You analyze camera information and decide actions.
Focus on environmental awareness.
""",

        "chat_assistant": """
You are a conversational AI assistant integrated into a robot.
Respond concise but helpful.
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

        "vision": """
Analyze environment and suggest next action.
"""
    }

    @classmethod
    def build_prompt(cls, mode: str, task: str, schema: str, user_input: str) -> str:

        system_prompt = cls.SYSTEM_PROMPTS.get(mode, "")
        task_prompt = cls.TASK_PROMPTS.get(task, "")

        return f"""
{system_prompt}

{task_prompt}

{schema}

User Input:
{user_input}
"""