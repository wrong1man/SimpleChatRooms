#!/bin/sh
#sleep 10
python manage.py makemigrations
python manage.py migrate
uvicorn SimpleChatRooms.asgi:application --host 0.0.0.0 --port 8000
