#!/usr/bin/env python
import os
import django
from django.conf import settings

# Django ni sozlash
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

print("🔍 Environment Variables:")
print(f"SAYQAL_USERNAME: {getattr(settings, 'SAYQAL_USERNAME', 'NOT SET')}")
print(f"SAYQAL_TOKEN: {getattr(settings, 'SAYQAL_TOKEN', 'NOT SET')}")
print(f"SAYQAL_NICKNAME: {getattr(settings, 'SAYQAL_NICKNAME', 'NOT SET')}")

print("\n🔍 System Environment:")
print(f"os.getenv('SAYQAL_USERNAME'): {os.getenv('SAYQAL_USERNAME', 'NOT SET')}")
print(f"os.getenv('SAYQAL_TOKEN'): {os.getenv('SAYQAL_TOKEN', 'NOT SET')}")
print(f"os.getenv('SAYQAL_NICKNAME'): {os.getenv('SAYQAL_NICKNAME', 'NOT SET')}")

print("\n🔍 .env file mavjudmi:")
env_file = os.path.join(os.path.dirname(__file__), '.env')
print(f".env file path: {env_file}")
print(f".env exists: {os.path.exists(env_file)}")

if os.path.exists(env_file):
    print("\n📋 .env file contents:")
    with open(env_file, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                print(f"  {line.strip()}")
