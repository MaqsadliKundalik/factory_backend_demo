import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

from apps.drivers.models import Driver
from django.contrib.auth.hashers import check_password

def verify_hashing():
    print("Testing auto-hashing...")
    
    # Create a test driver
    test_driver = Driver(
        name="Test Driver",
        phone_number="+998901234567",
        password="plain_password",
        car_type="car",
        car_number="01A777AA"
    )
    test_driver.save()
    
    print(f"Stored password: {test_driver.password[:20]}...")
    
    # Verify it is hashed
    is_hashed = test_driver.password.startswith('pbkdf2_sha256$')
    print(f"Is hashed? {is_hashed}")
    
    # Verify password works
    password_correct = check_password("plain_password", test_driver.password)
    print(f"Password correct? {password_correct}")
    
    # Cleanup
    test_driver.delete()
    
    if is_hashed and password_correct:
        print("Verification SUCCESS")
    else:
        print("Verification FAILED")

if __name__ == "__main__":
    verify_hashing()
