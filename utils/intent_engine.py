from typing import Dict
from rapidfuzz import process, fuzz
import re


class IntentEngine:

    def __init__(self):

        # Natural language patterns for each intent
        self.intent_patterns = {
            "chat": [
                "hello",
                "how are you",
                "what is",
                "tell me",
                "explain this",
                "who are you"
            ],
            "capture_image": [
                "take a photo",
                "capture image",
                "click picture",
                "take snapshot",
                "open camera"
            ],
            "movement": [
                "move forward",
                "go back",
                "turn left",
                "turn right",
                "rotate",
                "drive forward",
                "go ahead"
            ],
            "stop": [
                "stop",
                "halt",
                "freeze",
                "wait there"
            ]
        }

        self.threshold = 60  # minimum similarity score

    # ===================================
    # DETECT INTENT USING RAPIDFUZZ
    # ===================================

    def detect_intent(self, text: str) -> Dict:

        text = text.lower()

        best_intent = None
        best_score = 0

        for intent, patterns in self.intent_patterns.items():

            match, score, _ = process.extractOne(
                text,
                patterns,
                scorer=fuzz.partial_ratio
            )

            if score > best_score:
                best_score = score
                best_intent = intent

        if best_score < self.threshold:
            best_intent = "chat"

        return {
            "intent": best_intent,
            "confidence": round(best_score / 100, 2)
        }

    # ===================================
    # MOVEMENT PARAMETER EXTRACTION
    # ===================================

    def extract_movement_parameters(self, text: str) -> Dict:

        text = text.lower()

        direction = None
        speed = 1.0

        if "forward" in text:
            direction = "forward"
        elif "back" in text:
            direction = "backward"
        elif "left" in text:
            direction = "left"
        elif "right" in text:
            direction = "right"

        # Extract speed value (if mentioned)
        speed_match = re.search(r"\d+(\.\d+)?", text)
        if speed_match:
            speed = float(speed_match.group())

        return {
            "direction": direction,
            "speed": speed
        }


# ===================================
# TEST RUNNER
# ===================================

if __name__ == "__main__":

    engine = IntentEngine()

    while True:
        user_input = input("\nEnter command: ")

        result = engine.detect_intent(user_input)
        print("Intent:", result)

        if result["intent"] == "movement":
            movement_data = engine.extract_movement_parameters(user_input)
            print("Movement Params:", movement_data)