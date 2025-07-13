import whisper
import tempfile
import os

# Load Whisper model once
model = whisper.load_model("base")

def transcribe_audiofile(audio_bytes: bytes) -> str:
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    result = model.transcribe(tmp_path)
    transcript = result["text"]

    os.remove(tmp_path)
    return transcript
