from django.db import models
import uuid

class Meeting(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, blank=True, default="Untitled Meeting")
    audio_file = models.FileField(upload_to='meetings/audio/')
    transcript = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class ActionItem(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name='action_items')
    description = models.TextField()
    assignee = models.CharField(max_length=100, blank=True, null=True)
    due_date = models.CharField(max_length=50, blank=True, null=True)  # keep flexible
    priority = models.CharField(max_length=20, default='Medium')

    def __str__(self):
        return self.description[:60]