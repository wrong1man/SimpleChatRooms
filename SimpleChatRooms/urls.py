"""
URL configuration for SimpleChatRooms project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from messaging.views import *
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),

]

urlpatterns += [
   path("", index),
   path("register/", register),
   path("login/", login_user),
    path("logout/", logout_user),
   path("profile/", profile),
    path("start_chat/",get_start_Chat),
    path("load_previous_messages/", load_previous_messages)
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, show_indexes=True)
