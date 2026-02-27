from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.whouse_manager.models import WhouseManager
from data.whouse.models import Whouse
import os

class Command(BaseCommand):
    help = 'Create a superuser and WhouseManager if they do not exist'

    def handle(self, *args, **options):
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        phone = os.environ.get('DJANGO_SUPERUSER_PHONE', '+998912223344')

        # 1. Standard Django Superuser (for /admin/)
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, password=password, email=email)
            self.stdout.write(self.style.SUCCESS(f'Successfully created Django superuser: {username}'))
        
        # 2. WhouseManager (for Unified Login)
        manager = WhouseManager.objects.filter(phone_number=phone).first()
        if not manager:
            # Create a default warehouse if none exist
            whouse = Whouse.objects.first()
            if not whouse:
                whouse = Whouse.objects.create(name="Default Warehouse")
            
            manager = WhouseManager.objects.create(
                name="Admin Manager",
                phone_number=phone
            )
            manager.set_password(password)
            manager.save()
            manager.whouses.add(whouse)
            self.stdout.write(self.style.SUCCESS(f'Successfully created WhouseManager: {phone}'))
        else:
            # Force update password to match environment
            manager.set_password(password)
            manager.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated WhouseManager password: {phone}'))
