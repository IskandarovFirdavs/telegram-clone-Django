from django.contrib.auth.models import AbstractUser
from django.db import models


class UserModel(AbstractUser):
    pass


class Room(models.Model):
    CHAT_TYPE_CHOICES = [
        ('private', 'Private'),
        ('public', 'Public'),
    ]
    room_name = models.CharField(max_length=100, unique=True)
    members = models.ManyToManyField(UserModel, related_name='chats')
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES, default='public')

    def __str__(self):
        return self.room_name

    def can_add_member(self):
        if self.chat_type != 'private':
            return True
        if self.chat_type == 'private' and self.members.count() < 2:
            return True
        return False


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    message = models.CharField(max_length=255, null=True, blank=True)
    sender = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='chat', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.sender} -> {self.room}'


class ReplyMessage(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='reply')
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='reply')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reply')
    reply_message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.owner} -> {self.reply_message}'



class Notification(models.Model):
    owner = models.ForeignKey(UserModel, on_delete=models.CASCADE, related_name='notifications_owner')
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='noti')
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)


