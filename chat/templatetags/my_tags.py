import django_filters
from django import template

from chat.models import Room

register = template.Library()

@register.filter
def split_after_second_underscore(room_name, request):
    parts = room_name.split('_')
    if len(parts) > 2:
        if parts[2] == request.user.username:
            return parts[1]
        else:
            return parts[2]
    return room_name


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Room
        fields = ['chat_type']
