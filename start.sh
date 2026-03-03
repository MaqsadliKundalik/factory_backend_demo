#!/bin/bash

# Reset database (one-time fix for migration inconsistency)
echo "Resetting database..."
python full_reset_db.py

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Create superuser if it doesn't exist
echo "Setting up admin user..."
python manage.py setup_admin

# Start Gunicorn
echo "Starting Gunicorn..."
gunicorn app.wsgi:application --bind 0.0.0.0:8000
