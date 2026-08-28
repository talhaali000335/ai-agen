import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_path):
    """Transcribe audio using Groq's Whisper API."""
    with open(file_path, "rb") as audio_file:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",       # or "whisper-large-v3-turbo"
            file=audio_file,
            response_format="text",
        )
    return response.strip()

    print("TRANSCRIPT:", response)   # ✅ add this
    return response.strip()

def extract_meeting_details(transcript):
    prompt = f"""
You are an AI meeting assistant. Given the meeting transcript below, extract the following information in JSON format:

{{
  "summary": "A concise 2-3 sentence summary of the meeting.",
  "action_items": [
    {{
      "description": "Action item description",
      "assignee": "Person responsible (if mentioned, else null)",
      "due_date": "Due date (if mentioned, else null)",
      "priority": "High/Medium/Low"
    }}
  ]
}}

Meeting Transcript:
{transcript}

Only return valid JSON, nothing else.
"""
    response = groq_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=800,
    )
    content = response.choices[0].message.content.strip()
    content = content.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(content)
        return data
    except Exception:
        return {"summary": "", "action_items": []}