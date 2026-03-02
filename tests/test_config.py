"""
Test Configuration

Customize test behavior by modifying this file.
"""

# ==========================
# SPEECH-TO-TEXT SETTINGS
# ==========================

STT_CONFIG = {
    # Model size: tiny, base, small, medium, large-v3
    "model_size": "base",
    
    # Device: cpu, cuda, auto
    "device": "cpu",
    
    # Compute type: int8 (fast CPU), float16 (GPU), float32 (accurate)
    "compute_type": "int8",
    
    # Default recording duration (seconds)
    "default_duration": 5,
    
    # Sample rate (Hz)
    "sample_rate": 16000,
}


# ==========================
# INTENT DETECTION SETTINGS
# ==========================

INTENT_CONFIG = {
    # Confidence threshold (0-100)
    "threshold": 60,
    
    # Try local intent first if confidence > this
    "use_local_first": True,
}


# ==========================
# VISION SETTINGS
# ==========================

VISION_CONFIG = {
    # Camera index (0 = default camera)
    "camera_index": 0,
    
    # Image capture format
    "image_format": "jpg",
    
    # Save captured images
    "save_images": True,
    
    # Image output directory
    "image_dir": "captured_images",
    
    # Show annotated frames in test
    "show_annotations": True,
}


# ==========================
# AI ENGINE SETTINGS
# ==========================

AI_CONFIG = {
    # Model: models/gemini-2.5-flash
    "model": "models/gemini-2.5-flash",
    
    # Temperature (0.0 = deterministic, 1.0 = random)
    "temperature": 0.2,
    
    # Max retries on failure
    "max_retries": 2,
    
    # Timeout in seconds
    "timeout": 30,
}


# ==========================
# TEST SETTINGS
# ==========================

TEST_CONFIG = {
    # Verbose output
    "verbose": True,
    
    # Save test results
    "save_results": True,
    
    # Result output directory
    "results_dir": "test_results",
    
    # Test timeout (seconds)
    "test_timeout": 60,
    
    # Number of retries on failure
    "retries": 1,
}


# ==========================
# DEMO SETTINGS
# ==========================

DEMO_CONFIG = {
    # Recording duration for demos (seconds)
    "recording_duration": 5,
    
    # Number of conversation turns
    "conversation_turns": 3,
    
    # Show full JSON responses
    "show_json": True,
    
    # Print timing info
    "show_timing": True,
}


# ==========================
# COMPONENT TEST SAMPLES
# ==========================

# Sample sentences for intent testing
INTENT_TEST_SAMPLES = [
    "Hello, how are you?",
    "Tell me about robots",
    "Move forward quickly",
    "Go backward slowly",
    "Turn left",
    "Turn right",
    "Take a photo",
    "Capture an image",
    "Stop immediately",
    "What time is it?",
]

# Sample messages for chat testing
CHAT_TEST_SAMPLES = [
    "Hello! How are you?",
    "Tell me about artificial intelligence",
    "What can you help me with?",
    "How do robots work?",
    "What's the weather like?",
]

# Sample vision queries
VISION_TEST_QUERIES = [
    "Analyze this image in detail",
    "What objects do you see?",
    "Describe the environment",
    "Are there any people?",
    "What's the main focus?",
]


# ==========================
# HELPER FUNCTIONS
# ==========================

def get_stt_config():
    """Get speech-to-text configuration."""
    return STT_CONFIG


def get_vision_config():
    """Get vision configuration."""
    return VISION_CONFIG


def get_ai_config():
    """Get AI engine configuration."""
    return AI_CONFIG


def get_test_config():
    """Get test configuration."""
    return TEST_CONFIG


def get_demo_config():
    """Get demo configuration."""
    return DEMO_CONFIG


def get_intent_samples():
    """Get intent detection test samples."""
    return INTENT_TEST_SAMPLES


def get_chat_samples():
    """Get chat test samples."""
    return CHAT_TEST_SAMPLES


def get_vision_queries():
    """Get vision analysis queries."""
    return VISION_TEST_QUERIES


if __name__ == "__main__":
    # Print all configurations
    print("📋 Test Configuration")
    print("=" * 60)
    print("\n🎙️  Speech-to-Text Config:")
    print(f"   Model: {STT_CONFIG['model_size']}")
    print(f"   Device: {STT_CONFIG['device']}")
    print(f"   Duration: {STT_CONFIG['default_duration']}s")
    
    print("\n📸 Vision Config:")
    print(f"   Camera: {VISION_CONFIG['camera_index']}")
    print(f"   Format: {VISION_CONFIG['image_format']}")
    print(f"   Directory: {VISION_CONFIG['image_dir']}")
    
    print("\n🤖 AI Config:")
    print(f"   Model: {AI_CONFIG['model']}")
    print(f"   Temperature: {AI_CONFIG['temperature']}")
    print(f"   Max Retries: {AI_CONFIG['max_retries']}")
    
    print("\n🧪 Test Config:")
    print(f"   Verbose: {TEST_CONFIG['verbose']}")
    print(f"   Save Results: {TEST_CONFIG['save_results']}")
    
    print("\n" + "=" * 60)
    print("✅ Configuration loaded successfully!\n")
