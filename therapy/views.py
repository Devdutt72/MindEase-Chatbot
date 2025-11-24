from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.utils import timezone
from .models import Conversation, Message
from .services import AIService
from asgiref.sync import sync_to_async
import asyncio

# --- Database Helpers (Sync to Async) ---
@sync_to_async
def save_message(conversation_id, sender, content, is_crisis=False):
    """Saves a message to the database safely."""
    conversation = Conversation.objects.get(id=conversation_id)
    return Message.objects.create(
        conversation=conversation,
        sender=sender,
        content=content,
        is_crisis=is_crisis
    )

@sync_to_async
def get_or_create_conversation(user):
    """Gets the active chat session."""
    conversation, _ = Conversation.objects.get_or_create(
        user=user, 
        is_active=True,
        defaults={'title': f"Session {timezone.now().date()}"}
    )
    return conversation

# --- Service Wrappers (The Fix for Event Loop) ---
@sync_to_async
def check_safety_async(text):
    """Wraps the blocking safety check in an async thread."""
    return AIService.check_safety(text)

# --- Main Chat View ---
async def chat_view(request):
    # 1. Setup Dummy User (Async friendly)
    from django.contrib.auth.models import User
    user = await sync_to_async(User.objects.first)() 
    if not user:
        user = await sync_to_async(User.objects.create_superuser)('admin', 'admin@example.com', 'pass')

    conversation = await get_or_create_conversation(user)

    # 2. Handle Message Submission (HTMX POST)
    if request.method == "POST":
        user_text = request.POST.get('message')
        
        if user_text:
            # A. Save User Message
            await save_message(conversation.id, 'user', user_text)
            
            # B. Check Safety (Using the async wrapper)
            is_safe, reason = await check_safety_async(user_text)
            
            if not is_safe:
                # CRISIS PROTOCOL
                await save_message(conversation.id, 'ai', "Crisis Protocol Initiated", is_crisis=True)
                return render(request, 'partials/crisis_card.html')

            # C. If Safe, Trigger the Stream
            # We return a temporary bubble that connects to the stream URL
            context = {'conversation_id': conversation.id, 'user_text': user_text}
            return render(request, 'partials/ai_loader.html', context)

    # 3. Initial Page Load
    return render(request, 'chat.html')

# --- Streaming Logic (SSE) ---
async def stream_response(request, conversation_id):
    """
    Handles the Server-Sent Events (SSE) stream.
    """
    user_text = request.GET.get('text')
    
    async def event_stream():
        # VARIABLE TO HOLD THE FULL SENTENCE
        full_response = ""
        
        # We manually iterate the sync generator
        generator = AIService.generate_response(user_text)
        
        try:
            for token in generator:
                # 1. APPEND NEW WORD TO HISTORY
                full_response += token
                
                # 2. SEND THE WHOLE HISTORY SO FAR
                # This ensures "Hello" stays when "World" arrives
                yield f"data: {full_response}\n\n"
                
                # Tiny sleep to allow the browser to render smoothly
                await asyncio.sleep(0.02) 
            
            # Save the final complete message to DB
            await save_message(conversation_id, 'ai', full_response)
            
            # Send close event
            yield "event: close\ndata: \n\n"
            
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
            yield "event: close\ndata: \n\n"

    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')