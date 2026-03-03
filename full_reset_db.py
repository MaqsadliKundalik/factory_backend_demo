import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

def drop_all_tables():
    with connection.cursor() as cursor:
        print("Dropping all tables in public schema...")
        cursor.execute("""
            DO $$ DECLARE
                r RECORD;
            BEGIN
                FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
                    EXECUTE 'DROP TABLE IF EXISTS ' || quote_ident(r.tablename) || ' CASCADE';
                END LOOP;
            END $$;
        """)
        print("Successfully dropped all tables.")

if __name__ == "__main__":
    drop_all_tables()
