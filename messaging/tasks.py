from celery import shared_task
from .models import Conversation, Message, Generic_Activity_Log, Generic_Error_Log
import traceback


@shared_task
def add_message_to_conversation(convo_id,message_text,sender,timestamp):
    conversation = Conversation.objects.get(id=convo_id)
    msg=Message.objects.create(sender_id=sender,conversation=conversation,content=message_text,timestamp=timestamp)
    Generic_Activity_Log.objects.create(user_id=sender, type=3, content=f"Message id: {msg.id}", timestamp=timestamp)
    return


@shared_task
def log_activity(user_id, content, timestamp):
    Generic_Activity_Log.objects.create(user_id=user_id, type=2, content=content, timestamp=timestamp)


@shared_task
def log_error(user_id, content, function, timestamp):
    Generic_Error_Log.objects.create(user_id=user_id, type=3, content=content, function=function, timestamp=timestamp)