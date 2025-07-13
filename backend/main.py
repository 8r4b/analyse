# main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from transcriber import transcribe_audiofile
from analyzer import analyze_transcript

app = FastAPI()

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcript = transcribe_audiofile(audio_bytes)
    return {"transcript": transcript}

@app.post("/analyze")
async def analyze_audio(file: UploadFile = File(...)):
    audio_bytes = await file.read()
    transcript = transcribe_audiofile(audio_bytes)
    analysis = analyze_transcript(transcript)
    return {
        "transcript": transcript,
        **analysis
    }

