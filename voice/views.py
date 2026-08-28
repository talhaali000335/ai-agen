import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .services import transcribe_audio, generate_answer, text_to_speech

def voice_home(request):
    return render(request, 'voice.html')

@csrf_exempt
def process_voice(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST only'}, status=405)

    audio_file = request.FILES.get('audio')
    if not audio_file:
        return JsonResponse({'error': 'No audio file'}, status=400)

    # Save temporary file
    temp_path = os.path.join('media', 'temp_audio', audio_file.name)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, 'wb+') as f:
        for chunk in audio_file.chunks():
            f.write(chunk)

    try:
        transcript = transcribe_audio(temp_path)
        language = request.POST.get('language', 'en')
        answer = generate_answer(transcript, language)
        tts_url = text_to_speech(answer, language)
        return JsonResponse({
            'transcript': transcript,
            'answer': answer,
            'audio_url': tts_url,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)