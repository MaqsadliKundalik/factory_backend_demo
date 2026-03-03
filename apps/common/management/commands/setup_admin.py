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
                whouse=whouse,
                is_active=True,
                # Set all permissions to True for superuser
                crud_whouse_manager=True,
                crud_factory_operator=True,
                crud_driver=True,
                crud_guard=True,
                crud_product=True,
                crud_transport=True,
                crud_client=True,
                read_whouse=True,
                read_whouse_manager=True,
                read_factory_operator=True,
                read_driver=True,
                read_guard=True,
                read_product=True,
                read_transport=True,
                read_client=True
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created FactoryUser (Superuser): {phone}'))
        else:
            user.set_password(password)
            user.is_superuser = True
            user.is_staff = True
            user.role = 'manager'
            user.whouse = whouse
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated FactoryUser (Superuser): {phone}'))
