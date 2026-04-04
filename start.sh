#!/bin/bash
set -e

python manage.py migrate --noinput
python manage.py collectstatic --noinput

# Start Django server in background
gunicorn app.wsgi:application --bind 0.0.0.0:8000 --workers 2 &
DJANGO_PID=$!

# Start Telegram bot in background
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
import django
django.setup()
from tg_bot import Bot
bot = Bot()
bot.run()
" &
BOT_PID=$!

# Wait for both processes
wait $DJANGO_PID $BOT_PID
