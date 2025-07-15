from dotenv import load_dotenv
import os
import json
from openai import OpenAI

# Load environment variables
load_dotenv()

# Get API Key safely
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment variables.")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def analyze_transcript(transcript: str) -> dict:
    """
    Sends the transcript to OpenAI's chat model and returns structured analysis as a Python dict.
    """
    prompt = f"""
You are an AI assistant that evaluates interview answers for a job application. Analyze the following transcript and respond only with a JSON object containing:

- sentiment: Positive, Neutral, or Negative
- sentiment_score: float between -1 and 1
- readability_score: integer 0–100
- confidence_score: integer 0–100
- overall_score: integer 0–100
- summary: concise string
- suggestions: list of improvement suggestions

Transcript:
\"\"\"{transcript}\"\"\"
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an interview analyzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=500
        )

        # Get model's reply
        content = response.choices[0].message.content.strip()

        # Convert JSON string to Python dict
        analysis = json.loads(content)
        return analysis

    except Exception as e:
        return {
            "sentiment": "N/A",
            "sentiment_score": None,
            "readability_score": None,
            "confidence_score": None,
            "overall_score": None,
            "summary": f"Error analyzing transcript: {str(e)}",
            "suggestions": []
        }
