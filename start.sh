#!/bin/bash

# Generate migrations if they are missing
echo "Generating database migrations..."
python manage.py makemigrations --noinput

# Optional: Clean database if CLEAN_DATABASE=true
if [ "$CLEAN_DATABASE" = "true" ]; then
    echo "Cleaning database (flush)..."
    python manage.py flush --noinput
fi

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Setting up admin user..."
python manage.py setup_admin

# Start Gunicorn
echo "Starting Gunicorn..." 
gunicorn app.wsgi:application --bind 0.0.0.0:8000
