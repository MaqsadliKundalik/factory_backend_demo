from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data.whouse.models import Whouse
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser and FactoryUser if they do not exist'

    def handle(self, *args, **options):
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')
        phone = os.environ.get('DJANGO_SUPERUSER_PHONE', '+998912223344')
        name = os.environ.get('DJANGO_SUPERUSER_NAME', 'Admin Manager')

        # Create a default warehouse if none exist
        whouse = Whouse.objects.first()
        if not whouse:
            whouse = Whouse.objects.create(name="Default Warehouse")

        user = User.objects.filter(phone_number=phone).first()
        if not user:
            user = User.objects.create_superuser(
                phone_number=phone,
                password=password,
                name=name,
                role='manager',
                # whouses cannot be passed to create_superuser directly (M2M)
                is_active=True,
                # Set all permissions to True for superuser
                MAIN_PAGE=True,
                PRODUCTS_PAGE=True,
                ORDERS_PAGE=True,
                TRANSPORTS_PAGE=True,
                CLIENTS_PAGE=True,
                USERS_PAGE=True,
                READY_PRODUCTS_PAGE=True,
                DRIVERS_PAGE=True,
            )
            user.whouses.add(whouse)
            self.stdout.write(self.style.SUCCESS(f'Successfully created FactoryUser (Superuser): {phone}'))
        else:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.role = 'manager'
            user.whouses.add(whouse)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated FactoryUser (Superuser): {phone}'))
