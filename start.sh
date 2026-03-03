#!/bin/bash

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput --fake-initial

# Create superuser if it doesn't exist
echo "Setting up admin user..."
python manage.py setup_admin

# Start Gunicorn
echo "Starting Gunicorn..." 
gunicorn app.wsgi:application --bind 0.0.0.0:8000
