import requests
import sys

BASE_URL = "http://localhost:8002"
PHONE = "+998912223344"
PASSWORD = "admin123"

def test_api():
    print(f"Testing API at {BASE_URL}...")
    
    # 1. Login
    login_url = f"{BASE_URL}/auth/web/login/"
    payload = {
        "phone_number": PHONE,
        "password": PASSWORD,
        "platform": "web"
    }
    
    try:
        response = requests.post(login_url, json=payload)
        response.raise_for_status()
        data = response.json()
        token = data.get("access_token") # Corrected key
        if not token:
            print(f"✗ Login succeeded but no access_token found. Response: {data}")
            return
        print("✓ Login successful.")
    except Exception as e:
        print(f"✗ Login failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get Profile
    try:
        profile_url = f"{BASE_URL}/auth/web/me/"
        response = requests.get(profile_url, headers=headers)
        response.raise_for_status()
        print("✓ Profile retrieval successful.")
        # print(response.json())
    except Exception as e:
        print(f"✗ Profile retrieval failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

    # 3. List Warehouses
    try:
        wh_url = f"{BASE_URL}/whouse/"
        response = requests.get(wh_url, headers=headers)
        response.raise_for_status()
        print("✓ Warehouse listing successful.")
    except Exception as e:
        print(f"✗ Warehouse listing failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

    # 4. Create a test product type (CRUD test)
    try:
        pt_url = f"{BASE_URL}/products/types/"
        response = requests.post(pt_url, headers=headers, json={"name": "Test Type"})
        if response.status_code == 201:
            print("✓ Product Type creation successful.")
        else:
            print(f"✗ Product Type creation failed: {response.status_code} {response.text}")
    except Exception as e:
        print(f"✗ Product Type creation failed: {e}")
        if 'response' in locals():
            print(f"Response: {response.text}")

if __name__ == "__main__":
    test_api()
