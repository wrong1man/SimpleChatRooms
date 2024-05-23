from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Conversation)
admin.site.register(Message)
admin.site.register(Generic_Error_Log)
admin.site.register(Generic_Activity_Log)