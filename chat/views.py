from datetime import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Conversation, Message

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
        ).order_by("-timestamp").first()

        user_last_messages.append({
            "user": other_user,
            "last_message": last_message,
        })

    min_date = datetime.min
    if timezone.get_current_timezone() is not None:
        if not timezone.is_aware(min_date):
            min_date = timezone.make_aware(min_date)

    user_last_messages.sort(
        key=lambda x: x["last_message"].timestamp if x["last_message"] else min_date,
        reverse=True,
    )
    return user_last_messages


def _ensure_receiver_in_list(user_last_messages, receiver):
    for item in user_last_messages:
        if item["user"] == receiver:
            return user_last_messages
    user_last_messages.insert(0, {"user": receiver, "last_message": None})
    return user_last_messages


@login_required
def chat_index(request):
    user_last_messages = _get_user_last_messages(request.user)
    return render(request, "chat/chat.html", {
        "room_name": None,
        "chats": [],
        "user_last_messages": user_last_messages,
        "search_query": "",
    })


@login_required
def chat_list(request):
    room_name = request.GET.get("room", "")
    user_last_messages = _get_user_last_messages(request.user)
    return render(request, "chat/partials/chat_list.html", {
        "room_name": room_name,
        "user_last_messages": user_last_messages,
    })


@login_required
def chat_room(request, room_name):
    receiver = get_object_or_404(User, username=room_name)
    if receiver == request.user:
        return redirect("chat:index")

    search_query = request.GET.get("search", "")
    chats = Message.objects.filter(
        (Q(sender=request.user) & Q(receiver__username=room_name)) |
        (Q(receiver=request.user) & Q(sender__username=room_name))
    )

    if search_query:
        chats = chats.filter(Q(content__icontains=search_query))

    chats = chats.order_by("timestamp")
    Message.objects.filter(
        receiver=request.user,
        sender=receiver,
        is_read=False,
    ).update(is_read=True, read_at=timezone.now())

    user_last_messages = _get_user_last_messages(request.user)
    user_last_messages = _ensure_receiver_in_list(user_last_messages, receiver)

    if request.headers.get("HX-Request") == "true":
        return render(request, "chat/partials/chat_panel.html", {
            "room_name": room_name,
            "chats": chats,
            "search_query": search_query,
        })

    return render(request, "chat/chat.html", {
        "room_name": room_name,
        "chats": chats,
        "user_last_messages": user_last_messages,
        "search_query": search_query,
    })


@login_required
def start_chat(request, username):
    receiver = get_object_or_404(User, username=username)
    if receiver == request.user:
        return redirect("chat:index")

    return redirect("chat:room", room_name=receiver.username)


@login_required
def delete_chat(request, room_name):
    receiver = get_object_or_404(User, username=room_name)
    if receiver == request.user:
        return redirect("chat:index")

    Message.objects.filter(
        (Q(sender=request.user) & Q(receiver=receiver)) |
        (Q(receiver=request.user) & Q(sender=receiver))
    ).delete()
    Conversation.objects.filter(
        Q(user1=request.user, user2=receiver) |
        Q(user1=receiver, user2=request.user)
    ).delete()
    messages.success(request, "Chat deleted.")
    return redirect("chat:index")
