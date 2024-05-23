from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Conversation(models.Model):
    participants=models.ManyToManyField(User, related_name="participants")#This allows for more than 2 participants!

    created=models.DateTimeField(auto_now_add=True)
    modified=models.DateTimeField(auto_now=True)

    def get_title(self):
        return self.participants.all()

class Message(models.Model):
    sender=models.ForeignKey(User, related_name="sender", on_delete=models.CASCADE)
    conversation=models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
    content=models.TextField()
    timestamp=models.DateTimeField()
    class Meta:
        ordering = ['-timestamp',]
log_types=(
    (1,"User authentication"), #login, register and logout
    (2,"Open conversation"), #open or creating conversations
    (3,"Sent message") #user sent a message
)
class Generic_Activity_Log(models.Model):
    type=models.IntegerField(choices=log_types)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content=models.TextField()
    timestamp=models.DateTimeField()