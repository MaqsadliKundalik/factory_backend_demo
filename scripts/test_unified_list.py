import requests
import json

# Local test URL
BASE_URL = "http://localhost:8002"

def test_unified_list():
    print("--- Unified User List Test ---")

    # 1. Login to get token
    login_url = f"{BASE_URL}/auth/web/login/"
    login_data = {
        "phone_number": "+998912223344",
        "password": "admin123"
    }

    res_login = requests.post(login_url, json=login_data)
    if res_login.status_code != 200:
        print("Login failed")
        return

    token = res_login.json()['access_token']
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Test Unified List
    list_url = f"{BASE_URL}/users/unified-list/"
    print(f"\nRequesting {list_url}...")
    res_list = requests.get(list_url, headers=headers)
    
    if res_list.status_code == 200:
        data = res_list.json()
        print(f"Status: {res_list.status_code}")
        print(f"Total Count: {data.get('count')}")
        print("Users (Page 1):")
        for user in data.get('results', []):
            print(f"- {user['name']} ({user['role']}) | Phone: {user['phone_number']}")
    else:
        print(f"Error: {res_list.status_code}")
        print(res_list.text)

if __name__ == "__main__":
    test_unified_list()
