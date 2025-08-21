from django.contrib import admin

from chat.models import Message, Room, UserModel

admin.site.register(Room)
admin.site.register(UserModel)
admin.site.register(Message)
