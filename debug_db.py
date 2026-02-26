import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factory.settings')
django.setup()

from apps.whouse_manager.models import WhouseManager
from apps.factory_operator.models import FactoryOperator

print("--- WHOUSE MANAGERS ---")
for m in WhouseManager.objects.all():
    print(f"ID: {m.id}, Name: {m.name}, Phone: '{m.phone_number}'")

print("\n--- FACTORY OPERATORS ---")
for o in FactoryOperator.objects.all():
    print(f"ID: {o.id}, Name: {o.name}, Phone: '{o.phone_number}'")
