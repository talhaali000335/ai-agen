import os
import uuid
from django.conf import settings
from groq import Groq
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def transcribe_audio(file_path):
    """Transcribe using Groq's Whisper API (fast, no local model)."""
    with open(file_path, "rb") as audio_file:
        response = groq_client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=audio_file,
            response_format="text",
        )
    return response.strip()

def generate_answer(question, language="en"):
    if language == "ur":
        prompt = f"صارف کا سوال: {question}\nبراہ کرم اردو میں جواب دیں۔"
    else:
        prompt = f"User question: {question}\nPlease answer in English."

    response = groq_client.chat.completions.create(
        model="qwen/qwen3.6-27b",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=500,
    )
    return response.choices[0].message.content

def text_to_speech(text, language="en"):
    tts = gTTS(text=text, lang=language)
    filename = f"voice_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(settings.MEDIA_ROOT, 'voice_responses', filename)
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    tts.save(filepath)
    return settings.MEDIA_URL + 'voice_responses/' + filename