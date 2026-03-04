from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from data.whouse.models import Whouse
from data.users.models import FactoryUser
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

        # 1. Handle Standard Django Admin Superuser
        admin_username = 'admin'
        admin_user = User.objects.filter(username=admin_username).first()
        if not admin_user:
            User.objects.create_superuser(
                username=admin_username,
                password=password,
                email='admin@factory.com'
            )
            self.stdout.write(self.style.SUCCESS(f'Successfully created standard Superuser: {admin_username}'))
        else:
            admin_user.set_password(password)
            admin_user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated standard Superuser: {admin_username}'))

        # 2. Handle FactoryUser
        f_user = FactoryUser.objects.filter(phone_number=phone).first()
        if not f_user:
            f_user = FactoryUser.objects.create(
                phone_number=phone,
                name=name,
                role='manager',
                is_active=True,
                is_staff=True,
                is_superuser=True,
                MAIN_PAGE=True,
                PRODUCTS_PAGE=True,
                ORDERS_PAGE=True,
                TRANSPORTS_PAGE=True,
                WHEREHOUSES_PAGE=True,
                CLIENTS_PAGE=True,
                USERS_PAGE=True,
                READY_PRODUCTS_PAGE=True,
                DRIVERS_PAGE=True,
            )
            f_user.set_password(password)
            f_user.save()
            f_user.whouses.add(whouse)
            self.stdout.write(self.style.SUCCESS(f'Successfully created FactoryUser: {phone}'))
        else:
            f_user.set_password(password)
            f_user.name = name
            f_user.role = 'manager'
            f_user.whouses.add(whouse)
            f_user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated FactoryUser: {phone}'))
