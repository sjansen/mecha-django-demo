from __future__ import absolute_import, unicode_literals

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer

channel_layer = get_channel_layer()


@shared_task
def announce(room_group_name, message):
    async_to_sync(channel_layer.group_send)(
        room_group_name, {"type": "chat_message", "message": message}
    )
