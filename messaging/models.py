from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Conversation(models.Model):
    participants=models.ManyToManyField(User, related_name="participants")#This allows for more than 2 participants!

    created=models.DateTimeField(auto_now_add=True)
    modified=models.DateTimeField(auto_now=True)