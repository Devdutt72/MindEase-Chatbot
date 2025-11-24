from django.contrib import admin
from .models import Conversation, Message, MoodLog

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'created_at', 'is_active')
    list_filter = ('created_at', 'is_active')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('conversation', 'sender', 'is_crisis', 'timestamp')
    list_filter = ('is_crisis', 'sender')

@admin.register(MoodLog)
class MoodLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'emotion_label', 'score', 'trigger_topic', 'timestamp')
    list_filter = ('emotion_label', 'score')