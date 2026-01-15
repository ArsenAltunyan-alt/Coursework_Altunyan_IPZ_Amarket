from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.contrib import messages
from .models import Message, Conversation
from django.db.models import Q
from datetime import datetime

User = get_user_model()

def _get_user_last_messages(request_user):
    conversations = Conversation.objects.filter(
        Q(user1=request_user) | Q(user2=request_user)
    ).select_related("user1", "user2")
    user_last_messages = []

    for conversation in conversations:
        other_user = conversation.get_other_user(request_user)
        last_message = Message.objects.filter(
            (Q(sender=request_user) & Q(receiver=other_user)) |
            (Q(receiver=request_user) & Q(sender=other_user))
        ).order_by('-timestamp').first()

        user_last_messages.append({
            'user': other_user,
            'last_message': last_message
        })

    min_date = datetime.min
    if timezone.get_current_timezone() is not None:
        if not timezone.is_aware(min_date):
            min_date = timezone.make_aware(min_date)

    user_last_messages.sort(
        key=lambda x: x['last_message'].timestamp if x['last_message'] else min_date,
        reverse=True
    )
    return user_last_messages

@login_required
def chat_index(request):
    user_last_messages = _get_user_last_messages(request.user)
    return render(request, 'chat/chat.html', {
        'room_name': None,
        'chats': [],
        'user_last_messages': user_last_messages,
        'search_query': ''
    })

@login_required
def chat_room(request, room_name):
    receiver = get_object_or_404(User, username=room_name)
    if receiver == request.user:
        return redirect('chat:index')

    has_conversation = Conversation.objects.filter(
        Q(user1=request.user, user2=receiver) |
        Q(user1=receiver, user2=request.user)
    ).exists()

    if not has_conversation:
        messages.info(request, 'Спочатку відкрийте чат через кнопку «Повідомлення».')
        return redirect('chat:index')

    search_query = request.GET.get('search', '') 
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))  

    chats = chats.order_by('timestamp') 
    user_last_messages = _get_user_last_messages(request.user)

    return render(request, 'chat/chat.html', {
        'room_name': room_name,
        'chats': chats,
        'user_last_messages': user_last_messages,
        'search_query': search_query 
    })

@login_required
def start_chat(request, username):
    receiver = get_object_or_404(User, username=username)
    if receiver == request.user:
        return redirect('chat:index')

    Conversation.get_or_create_between(request.user, receiver)
    return redirect('chat:room', room_name=receiver.username)
