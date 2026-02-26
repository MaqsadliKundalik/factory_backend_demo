import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'factory.settings')
django.setup()
settings.ALLOWED_HOSTS.append('testserver')

from django.test import Client
from apps.whouse_manager.models import WhouseManager
from apps.factory_operator.models import FactoryOperator
from apps.common.models import UserPermissions
import json

def test_flow():
    client = Client()
    phone = "+998912675782"
    password = "Odi@1234"

    print(f"--- Testing Login for {phone} ---")
    login_response = client.post('/auth/web/login/', 
                                data=json.dumps({"phone_number": phone, "password": password}),
                                content_type='application/json')
    
    if login_response.status_code != 200:
        print(f"FAILED: Login status {login_response.status_code}")
        print(login_response.content.decode())
        return

    data = login_response.json()
    access_token = data.get('access')
    print("SUCCESS: Logged in and received token")

    headers = {'HTTP_AUTHORIZATION': f'Bearer {access_token}'}

    print("\n--- Testing Profile API ---")
    profile_response = client.get('/auth/web/me/', **headers)
    print(f"STATUS: {profile_response.status_code}")
    if profile_response.status_code == 200:
        print(f"DATA: {profile_response.json()}")
    else:
        print(f"FAILED: {profile_response.content.decode()}")

    print("\n--- Testing User Permissions API ---")
    perms_response = client.get('/common/user-permissions/', **headers)
    print(f"STATUS: {perms_response.status_code}")
    if perms_response.status_code == 200:
        print(f"PERMISSIONS LIST: {len(perms_response.json())} items found")
    else:
        print(f"FAILED: {perms_response.content.decode()}")

    print("\n--- Testing Signal (Auto-permissions for new Operator) ---")
    # Verify signals
    new_op_phone = "+998991234567"
    # Cleanup if exists
    FactoryOperator.objects.filter(phone_number=new_op_phone).delete()
    
    from apps.whouse.models import Whouse
    whouse = Whouse.objects.first()
    
    new_op = FactoryOperator.objects.create(
        name="Test Operator",
        phone_number=new_op_phone,
        password="password123",
        whouse=whouse
    )
    print(f"SUCCESS: Created new operator {new_op.name}")
    
    perms = UserPermissions.objects.filter(object_id=str(new_op.id)).first()
    if perms:
        print("SUCCESS: Permissions automatically created via Signal")
        print(f"crud_whouse: {perms.crud_whouse}")
        print(f"crud_whouse_manager: {perms.crud_whouse_manager} (Should be False for Operator)")
    else:
        print("FAILED: Permissions NOT created automatically")

if __name__ == "__main__":
    test_flow()
