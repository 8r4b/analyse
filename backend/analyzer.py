from dotenv import load_dotenv
import os
from openai import OpenAI

load_dotenv()  # Load .env file variables

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not set in environment variables.")

client = OpenAI(api_key=api_key)

def analyze_transcript(transcript: str) -> dict:
    """
    Sends the transcript to OpenAI GPT chat model and returns structured analysis.
    """
    prompt = f"""
You are an AI assistant that evaluates interview answers for a job application. Analyze the following transcript and provide a JSON object with the fields:
- sentiment: Positive, Neutral, or Negative
- sentiment_score: float between -1 (negative) and 1 (positive)
- readability_score: an integer from 0 to 100
- confidence_score: an integer percentage from 0 to 100 reflecting how confident you are in the analysis
- overall_score: an integer from 0 to 100 reflecting overall candidate quality
- summary: a concise textual summary
- suggestions: a list of suggestions for improvement

Transcript:
\"\"\"{transcript}\"\"\"

Respond only with a JSON object.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": "You are an interview analyzer."},
                      {"role": "user", "content": prompt}],
            temperature=0.5,
            max_tokens=500
        )
        # The content of the assistant's message should be the JSON string
        content = response.choices[0].message.content.strip()

        # Convert content string to Python dict safely
        import json
        analysis = json.loads(content)
        return analysis

    except Exception as e:
        # If something goes wrong, return an error summary
        return {
            "sentiment": "N/A",
            "sentiment_score": None,
            "readability_score": None,
            "confidence_score": None,
            "overall_score": None,
            "summary": f"Error analyzing transcript: {str(e)}",
            "suggestions": []
        }
