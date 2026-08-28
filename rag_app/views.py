import json
import os
import re
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Document
from .services import add_to_vector_store, get_qa_chain

@csrf_exempt
def upload_document(request):
    if request.method == 'POST' and request.FILES.get('file'):
        file = request.FILES['file']
        title = request.POST.get('title', file.name)
        doc = Document.objects.create(title=title, file=file)
        file_path = doc.file.path
        try:
            chunk_count = add_to_vector_store(file_path)
            return JsonResponse({"message": f"Added {chunk_count} chunks to vector store."})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "No file provided"}, status=400)

@csrf_exempt
def rag_chat(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data.get('message', '')
        model = data.get('model', 'qwen/qwen3.6-27b')
        try:
            qa_chain = get_qa_chain(model)
            raw_answer = qa_chain.run(question)

            # Remove <think>...</think> blocks
            cleaned_answer = re.sub(r'<think>.*?</think>', '', raw_answer, flags=re.DOTALL)
            cleaned_answer = re.sub(r'<think.*?>', '', cleaned_answer)

            return JsonResponse({"answer": cleaned_answer.strip()})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({"error": "POST only"}, status=405)

def rag_home(request):
    return render(request, "rag_chat.html")