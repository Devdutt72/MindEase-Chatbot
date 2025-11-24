from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    """
    Stores the chat history container.
    'summary' field is the key to your 'Long-Term Memory' resume point.
    It holds the AI-generated recap of the session.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="conversations")
    title = models.CharField(max_length=200, default="New Conversation")
    summary = models.TextField(blank=True, null=True, help_text="AI-generated summary for long-term memory")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Message(models.Model):
    """
    Individual messages.
    'is_crisis' field powers your 'Safety Middleware' resume point.
    """
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Therapist'),
    ]

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    content = models.TextField()
    is_crisis = models.BooleanField(default=False, help_text="Flagged by Llama Guard safety layer")
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.content[:50]}..."

class MoodLog(models.Model):
    """
    The Data Analyst special.
    This table powers your 'Mood Analytics Dashboard'.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mood_logs")
    conversation = models.ForeignKey(Conversation, on_delete=models.SET_NULL, null=True, blank=True)
    
    # 1-10 Scale
    score = models.IntegerField() 
    
    # e.g., "Anxiety", "Joy", "Neutral"
    emotion_label = models.CharField(max_length=50)
    
    # e.g., "Work", "Family", "Exams" (Extracted by AI)
    trigger_topic = models.CharField(max_length=100, blank=True, null=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.emotion_label} ({self.score}/10)"