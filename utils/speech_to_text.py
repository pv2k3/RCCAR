import asyncio
import numpy as np
import sounddevice as sd
from faster_whisper import WhisperModel


class SpeechToText:

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8"
    ):
        """
        model_size: tiny, base, small, medium, large-v3
        device: cpu
        compute_type: int8 (fast CPU inference)
        """

        try:
            print("🔧 Initializing Whisper (CPU mode)...")
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type
            )
            print("✅ Whisper initialized successfully.")
        except Exception as e:
            raise RuntimeError(f"Failed to initialize Whisper model: {e}")

    def record_audio(self, duration: int = 5, sample_rate: int = 16000):
        """
        Record audio from microphone.
        """
        try:
            print(f"\n🎙 Recording for {duration} seconds...")
            audio = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=1,
                dtype="float32"
            )
            sd.wait()
            print("✅ Recording complete.")
            return audio.flatten(), sample_rate

        except Exception as e:
            raise RuntimeError(f"Audio recording failed: {e}")

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> str:
        """
        Convert audio to plain text.
        """
        try:
            segments, _ = self.model.transcribe(audio)

            full_text = ""
            for segment in segments:
                full_text += segment.text + " "

            return full_text.strip()

        except Exception as e:
            raise RuntimeError(f"Transcription failed: {e}")

    async def listen_and_transcribe(self, duration: int = 5) -> str:
        """
        Async wrapper for recording + transcription.
        """
        loop = asyncio.get_running_loop()

        audio, sample_rate = await loop.run_in_executor(
            None,
            self.record_audio,
            duration
        )

        return await loop.run_in_executor(
            None,
            self.transcribe,
            audio,
            sample_rate
        )


# ===============================
# TEST RUNNER
# ===============================

async def main():
    stt = SpeechToText(
        model_size="base",
        device="cpu",
        compute_type="int8"
    )

    text = await stt.listen_and_transcribe(duration=5)

    print("\n=== TRANSCRIBED TEXT ===")
    print(text)


if __name__ == "__main__":
    asyncio.run(main())