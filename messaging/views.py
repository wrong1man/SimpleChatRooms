from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import dateparse
from .forms import *
from .models import Conversation, Message
from django.http import HttpResponse
import json
def index(request):
    if request.user.is_authenticated:
        return redirect("profile/")
    else:
        return redirect("login/")
def register(request):
    if request.method == 'POST':
        # print(request.POST)
        user_form = BaseUserSerializer_form(data=request.POST)
        if user_form.is_valid():
            user = user_form.save()
            login(request,user)
            return redirect("/profile/")
        else:
            # print(user_form.errors)
            return render(request, "register.html", {"errors": json.loads(user_form.errors.as_json())})
    else:
        return render(request, "register.html")

def login_user(request):
    next=request.GET.get("next","/profile/")
    if request.user.is_authenticated:
        return redirect(next)
    if request.method =="GET":
        return render(request, "login.html")
    else:
        username=request.POST.get("username")
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect(next)
        else:
            return redirect("/login/?invalid=1&next="+next)
def logout_user(request):
    logout(request)
    return redirect("/")

@login_required
def profile(request):
    all_users=User.objects.all().exclude(id=request.user.id)
    mychats=Conversation.objects.filter(participants=request.user)
    return render(request, "profile.html", {"all_users":all_users, "mychats":mychats})
@login_required
def get_start_Chat(request):
    participant1=request.user
    participant2=request.GET.get("target_user")
    chat_id=request.GET.get("cid")
    convo=Conversation.objects.filter(id=chat_id).first()
    if convo:
        #opening conversation from ID
        if participant1 in convo.participants.all():
            pass
        else:
            return HttpResponse("Conversation not found.",status=404)
    elif Conversation.objects.filter(participants=participant1).filter(participants__id=participant2).exists():
        #opening conversation from "start chat" - First finds existing conversations
        convo=Conversation.objects.filter(participants=participant1).filter(participants__id=participant2).first()
    else:
        convo=Conversation.objects.create()
        convo.participants.add(participant1)
        convo.participants.add(participant2)
        convo.save()
    return render(request, "chat.html", {"conversation": convo})


@login_required
def load_previous_messages(request):
    cid=request.GET.get("cid")
    timestamp=dateparse.parse_datetime(request.GET.get("timestamp"))
    msgs=Message.objects.filter(conversation_id=cid, conversation__participants=request.user)#, timestamp__lt=timestamp)
    print(timestamp, cid)
    print(msgs)
    return