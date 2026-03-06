"""
Aura system configuration.
All settings are loaded from environment variables / .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration for the Aura system."""

    # ── LLM ──────────────────────────────────────────────────────────────────
    gemini_api_key: str = Field("", env="GEMINI_API_KEY")
    gemini_model: str = Field("models/gemini-2.5-flash", env="GEMINI_MODEL")
    llm_temperature: float = Field(0.2, env="LLM_TEMPERATURE")
    llm_max_retries: int = Field(2, env="LLM_MAX_RETRIES")

    # ── Vision ────────────────────────────────────────────────────────────────
    camera_index: int = Field(0, env="CAMERA_INDEX")
    yolo_model_path: str = Field("yolov8n.pt", env="YOLO_MODEL_PATH")
    vision_confidence_threshold: float = Field(0.5, env="VISION_CONFIDENCE_THRESHOLD")

    # ── Audio / STT ───────────────────────────────────────────────────────────
    whisper_model_size: str = Field("base", env="WHISPER_MODEL_SIZE")
    whisper_device: str = Field("cpu", env="WHISPER_DEVICE")
    whisper_compute_type: str = Field("int8", env="WHISPER_COMPUTE_TYPE")
    audio_sample_rate: int = Field(16000, env="AUDIO_SAMPLE_RATE")
    audio_record_duration: int = Field(5, env="AUDIO_RECORD_DURATION")

    # ── Audio / TTS ───────────────────────────────────────────────────────────
    tts_voice: str = Field("en-US-AriaNeural", env="TTS_VOICE")
    tts_rate: str = Field("+0%", env="TTS_RATE")
    tts_offline_fallback: bool = Field(False, env="TTS_OFFLINE_FALLBACK")

    # ── Wake Word ─────────────────────────────────────────────────────────────
    wake_word: str = Field("hey aura", env="WAKE_WORD")
    wake_word_threshold: float = Field(0.5, env="WAKE_WORD_THRESHOLD")

    # ── Robotics ──────────────────────────────────────────────────────────────
    serial_port: str = Field("", env="SERIAL_PORT")
    serial_baud_rate: int = Field(115200, env="SERIAL_BAUD_RATE")
    robotics_enabled: bool = Field(False, env="ROBOTICS_ENABLED")

    # RC car control mode: "simulation" | "serial" | "http"
    rc_control_type: str = Field("simulation", env="RC_CONTROL_TYPE")
    # Base URL of RC WiFi module (used when RC_CONTROL_TYPE=http)
    rc_control_url: str = Field("http://192.168.4.1", env="RC_CONTROL_URL")
    # RC car camera stream URL — empty string means use local CAMERA_INDEX
    rc_video_url: str = Field("", env="RC_VIDEO_URL")

    # ── Distance sensor ───────────────────────────────────────────────────────
    # True = generate dummy sensor data; False = read from RC HTTP endpoint
    dummy_sensor_data: bool = Field(True, env="DUMMY_SENSOR_DATA")
    # Stop the car if front obstacle is closer than this (cm)
    obstacle_stop_distance: float = Field(20.0, env="OBSTACLE_STOP_DISTANCE")
    # Follow mode: target distance window (cm)
    follow_distance_min: float = Field(50.0, env="FOLLOW_DISTANCE_MIN")
    follow_distance_max: float = Field(100.0, env="FOLLOW_DISTANCE_MAX")

    # ── Person tracking ───────────────────────────────────────────────────────
    # Fraction of frame width treated as "centered" — no turn command issued
    tracking_center_deadzone: float = Field(0.12, env="TRACKING_CENTER_DEADZONE")
    # bbox area / frame area thresholds to decide move forward / backward
    tracking_area_too_far: float = Field(0.04, env="TRACKING_AREA_TOO_FAR")
    tracking_area_too_close: float = Field(0.30, env="TRACKING_AREA_TOO_CLOSE")

    # ── API Server ────────────────────────────────────────────────────────────
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    api_enabled: bool = Field(True, env="API_ENABLED")

    # ── Logging ───────────────────────────────────────────────────────────────
    log_level: str = Field("INFO", env="LOG_LEVEL")

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


# Single shared instance imported across all modules
settings = Settings()
