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
activity_log_types=(
    (1,"User authentication"), #login, register and logout
    (2,"Conversation"), #onversation related - create, connect, disconnet, etc..
    (3,"Sent message") #user sent a message
)
class Generic_Activity_Log(models.Model):
    type=models.IntegerField(choices=activity_log_types)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content=models.TextField()
    timestamp=models.DateTimeField()

    def __str__(self):
        return f"{self.get_type_display()} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
error_log_types=(
    (1,"Views error"), #errors in view's methods
    (2,"Models error"), #errors in models's methods
    (3,"Services error") #errors with external services (redis, celery, etc)
)
class Generic_Error_Log(models.Model):
    type=models.IntegerField(choices=error_log_types)
    user=models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content=models.TextField()
    timestamp=models.DateTimeField()
    function=models.CharField(max_length=100)
    args=models.TextField()

    def __str__(self):
        return f"{self.get_type_display()}: {self.function} - {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
