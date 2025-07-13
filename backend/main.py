from fastapi import FastAPI, UploadFile, File, Depends, Security, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader
from sqlalchemy.orm import Session
from datetime import datetime
from dotenv import load_dotenv
import os

from transcriber import transcribe_audiofile
from analyzer import analyze_transcript
from database import SessionLocal
from models import RecordingSession

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Get API key and API key header name from env variables
API_KEY = os.getenv("API_KEY")
API_KEY_NAME = os.getenv("API_KEY_NAME", "access_token")  # Default header name if not set

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def get_api_key(api_key_header_value: str = Security(api_key_header)):
    if api_key_header_value == API_KEY:
        return api_key_header_value
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
        )

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcript = transcribe_audiofile(audio_bytes)
    return {"transcript": transcript}

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...), db: Session = Depends(get_db)):
    audio_bytes = await file.read()
    transcript = transcribe_audiofile(audio_bytes)
    analysis = analyze_transcript(transcript)

    # Save analysis and transcript to DB
    recording = RecordingSession(
        transcript=transcript,
        sentiment=analysis.get("sentiment"),
        sentiment_score=analysis.get("sentiment_score"),
        readability_score=analysis.get("readability_score"),
        confidence_score=analysis.get("confidence_score"),
        overall_score=analysis.get("overall_score"),
        summary=analysis.get("summary"),
        suggestions=analysis.get("suggestions"),
        created_at=datetime.utcnow()
    )
    db.add(recording)
    db.commit()
    db.refresh(recording)

    return {
        "transcript": transcript,
        **analysis,
        "id": recording.id
    }

@app.get("/recordings")
def get_recordings(db: Session = Depends(get_db), api_key: str = Depends(get_api_key)):
    recordings = db.query(RecordingSession).order_by(RecordingSession.created_at.desc()).all()
    return recordings
