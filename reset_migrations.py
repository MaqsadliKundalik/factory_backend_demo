import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

def clear_migrations():
    with connection.cursor() as cursor:
        print("Clearing django_migrations table...")
        cursor.execute("DELETE FROM django_migrations;")
        print("Successfully cleared django_migrations.")

if __name__ == "__main__":
    clear_migrations()
