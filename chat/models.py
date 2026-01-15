from django.db import models
from django.conf import settings

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_messages", on_delete=models.CASCADE)
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="received_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender} -> {self.receiver}: {self.content[:20]}"


class Conversation(models.Model):
    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="conversations_as_user1",
        on_delete=models.CASCADE,
    )
    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="conversations_as_user2",
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_conversation_pair",
            ),
        ]

    @staticmethod
    def _ordered_users(user_a, user_b):
        if user_a.id < user_b.id:
            return user_a, user_b
        return user_b, user_a

    @classmethod
    def get_or_create_between(cls, user_a, user_b):
        user1, user2 = cls._ordered_users(user_a, user_b)
        return cls.objects.get_or_create(user1=user1, user2=user2)

    def get_other_user(self, user):
        return self.user2 if self.user1 == user else self.user1
