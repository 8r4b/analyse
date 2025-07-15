import whisper
import tempfile
import os

# Use the smallest Whisper model to save memory
model = whisper.load_model("tiny")  # Or "base" if you're confident in RAM

def transcribe_audiofile(audio_bytes: bytes) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        result = model.transcribe(tmp_path)
        return result.get("text", "")

    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
