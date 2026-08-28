import json
import os
import re

from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from groq import Groq
from dotenv import load_dotenv
from .models import Conversation, Message

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

AVAILABLE_MODELS = [
    "qwen/qwen3.6-27b",
]

def home(request):
    return render(request, "index.html", {"models": AVAILABLE_MODELS})

@csrf_exempt
@require_http_methods(["POST"])
def chat(request):
    try:
        data = json.loads(request.body)
        user_message = data.get("message", "")
        model = data.get("model", AVAILABLE_MODELS[0])
        conversation_id = data.get("conversation_id")

        if model not in AVAILABLE_MODELS:
            return JsonResponse({"error": "Invalid model"}, status=400)

        if conversation_id:
            conversation = Conversation.objects.filter(id=conversation_id).first()
            if not conversation:
                conversation = Conversation.objects.create()
        else:
            conversation = Conversation.objects.create()

        Message.objects.create(
            conversation=conversation,
            role="user",
            content=user_message
        )

        previous_messages = conversation.messages.all()[:10]
        groq_messages = []
        for msg in previous_messages:
            groq_messages.append({
                "role": "user" if msg.role == "user" else "assistant",
                "content": msg.content,
            })

        response = StreamingHttpResponse(
            generate_response(groq_messages, model, conversation),
            content_type="text/plain",
        )
        response['X-Conversation-ID'] = str(conversation.id)
        return response

    except Exception as e:
        print("❌ VIEW ERROR:", e)
        return JsonResponse({"error": str(e)}, status=500)

def generate_response(messages, model, conversation):
    try:
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=1024,
        )
        raw_reply = ""
        for chunk in stream:
            token = chunk.choices[0].delta.content
            if token:
                raw_reply += token

        cleaned_reply = re.sub(r'<think>.*?</think>', '', raw_reply, flags=re.DOTALL)
        cleaned_reply = re.sub(r'<think.*?>.*?</think>', '', cleaned_reply, flags=re.DOTALL)
        cleaned_reply = re.sub(r'<think.*?>', '', cleaned_reply)

        Message.objects.create(
            conversation=conversation,
            role="assistant",
            content=cleaned_reply.strip()
        )
        yield cleaned_reply.strip()

    except Exception as e:
        yield f"\n[Error]: {str(e)}"

def list_conversations(request):
    conversations = Conversation.objects.order_by("-created_at")[:20]
    data = [
        {
            "id": conv.id,
            "title": conv.title,
            "created_at": conv.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for conv in conversations
    ]
    return JsonResponse(data, safe=False)