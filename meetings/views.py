import os
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from .models import Meeting, ActionItem
from .services import transcribe_audio, extract_meeting_details

def meetings_home(request):
    meetings = Meeting.objects.all().order_by('-created_at')
    return render(request, 'meetings.html', {'meetings': meetings})

@csrf_exempt
def upload_meeting(request):
    if request.method == 'POST' and request.FILES.get('audio_file'):
        audio_file = request.FILES['audio_file']
        title = request.POST.get('title', 'Untitled Meeting')
        meeting = Meeting.objects.create(title=title, audio_file=audio_file)
        
        try:
            file_path = meeting.audio_file.path
            # Transcribe
            transcript = transcribe_audio(file_path)
            meeting.transcript = transcript
            meeting.save()
            
            # Extract summary & action items
            result = extract_meeting_details(transcript)
            meeting.summary = result.get('summary', '')
            meeting.save()
            
            for item in result.get('action_items', []):
                ActionItem.objects.create(
                    meeting=meeting,
                    description=item.get('description', ''),
                    assignee=item.get('assignee'),
                    due_date=item.get('due_date'),
                    priority=item.get('priority', 'Medium'),
                )
            
            return JsonResponse({
                "meeting_id": str(meeting.id),
                "summary": meeting.summary,
                "action_items": list(meeting.action_items.values()),
                "transcript": meeting.transcript,          # ✅ add this
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "No audio file provided"}, status=400)

def meeting_detail(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    return JsonResponse({
        "title": meeting.title,
        "transcript": meeting.transcript,
        "summary": meeting.summary,
        "action_items": list(meeting.action_items.values()),
    })
