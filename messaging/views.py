from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import dateparse, timezone
from django.core import serializers
from django.http import JsonResponse
from .forms import *
from .models import Conversation, Message, Generic_Activity_Log, Generic_Error_Log
from django.http import HttpResponse
import json
import traceback
from celery.execute import send_task
def index(request):
    """
    Redirects to the profile page if the user is authenticated, otherwise redirects to the login page.
    """
    if request.user.is_authenticated:
        return redirect("profile/")
    else:
        return redirect("login/")
def register(request):
    """
    Registers a new user if the request method is POST. If the method is GET, it displays the registration page.
    """
    if request.method == 'POST':
        try:
            user_form = BaseUserSerializer_form(data=request.POST)
            stamp=timezone.now()
            if user_form.is_valid():
                user = user_form.save()
                user.set_password(request.POST['password'])
                user.save()
                login(request,user)

                Generic_Activity_Log.objects.create(user=user, type=1, content="User registered", timestamp=stamp)
                Generic_Activity_Log.objects.create(user=user, type=1,content="user login", timestamp=stamp)

                return redirect("/profile/")
            else:
                Generic_Activity_Log.objects.create(user=None, type=1, content=f"Failed to register user: {request.POST.get('username')}\nErrors:{user_form.errors.as_json()}", timestamp=stamp)
                return render(request, "register.html", {"errors": json.loads(user_form.errors.as_json())})
        except Exception as e:
            Generic_Error_Log.objects.create(
                type=1,
                user=request.user,
                content=traceback.format_exc() + f"\n{e}",
                timestamp=timezone.now(),
                function='register',
                args=f"username: {request.POST.get('username')}\n email: {request.POST.get('email')}\n"
            )
        return HttpResponse("An error occurred.", status=500)
    else:
        return render(request, "register.html")

def login_user(request):
    """
    Authenticates and logs in a user if the request method is POST. If the method is GET, it displays the login page.
    """
    next=request.GET.get("next","/profile/")
    if request.user.is_authenticated:
        return redirect(next)
    if request.method =="GET":
        return render(request, "login.html")
    else:
        username=request.POST.get("username")
        password=request.POST.get("password")
        user = authenticate(username=username, password=password)
        stamp=timezone.now()
        if user is not None:
            login(request, user)
            Generic_Activity_Log.objects.create(user=user, type=1,content="user login" ,timestamp=stamp)
            return redirect(next)
        else:
            Generic_Activity_Log.objects.create(user=None, type=1, content=f"Failed login attempt for user: {username}", timestamp=stamp)
            return render(request, "login.html", {"invalid":True})

@login_required
def logout_user(request):
    Generic_Activity_Log.objects.create(user=request.user, type=1, content="user logout", timestamp=timezone.now())
    logout(request)
    return redirect("/")

@login_required
def profile(request):
    all_users=User.objects.all().exclude(id=request.user.id)
    mychats=Conversation.objects.filter(participants=request.user)
    return render(request, "profile.html", {"all_users":all_users, "mychats":mychats})


# from celery import current_app
# from .tasks import log_activity


@login_required
def get_start_Chat(request):
    """
    Initiates a chat between the authenticated user and another user.
    If a chat already exists between the two users, that chat is used.
    Otherwise, a new chat is created.
    """
    participant1=request.user
    participant2=request.GET.get("target_user")
    chat_id=request.GET.get("cid")
    try: #No exceptions expected - using this try "just in case" and to show error logging.
        convo=Conversation.objects.filter(id=chat_id).first()#Filter+first is less prone to errors than get
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
            send_task('tasks.log_activity', args=(participant1.id, f"Open Chat. id# {convo.id}", timezone.now()))
        # current_app.send_task('messaging.tasks.log_activity',
        #                       (participant1.id, f"Open Chat. id# {convo.id}", timezone.now()))

        Generic_Activity_Log.objects.create(user=participant1, type=2, content=f"Open Chat. id# {convo.id}",timestamp=timezone.now())
        return render(request, "chat.html", {"conversation": convo})
    except Exception as e:
        Generic_Error_Log.objects.create(
            type=1,
            user=request.user,
            content=traceback.format_exc()+f"\n{e}",
            timestamp=timezone.now(),
            function='get_start_Chat',
            args=f"paticipant1: {participant1}\n paticipant2: {participant2}\n chat_id: {chat_id}"
        )
    return HttpResponse("An error occurred.", status=500)

@login_required
def load_previous_messages(request):
    """
    Loads previous messages for a given chat.
    """
    cid=request.GET.get("cid")
    try:
        timestamp=dateparse.parse_datetime(request.GET.get("timestamp"))
        msgs=Message.objects.filter(conversation_id=cid, conversation__participants=request.user, timestamp__lt=timestamp)
        serialized_obj = serializers.serialize('json', msgs)
        Generic_Activity_Log.objects.create(user=request.user, type=2, content=f"Request chat history. id# {cid}", timestamp=timezone.now())
        return JsonResponse(json.loads(serialized_obj), safe=False, content_type='application/json')
    except Exception as e:
        Generic_Error_Log.objects.create(
            type=1,
            user=request.user,
            content=traceback.format_exc() + f"\n{e}",
            timestamp=timezone.now(),
            function='load_previous_messages',
            args=f"chat_id: {cid}\n timestamp: {timestamp}\n"
        )
    return HttpResponse("An error occurred.", status=500)
