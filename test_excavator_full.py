import requests
from pprint import pprint
import time
import json
from datetime import datetime, timezone

# Set this to True to test against your local server, or False for Render
TEST_LOCAL = False

BASE_URL = "http://127.0.0.1:8001" if TEST_LOCAL else "https://factory-backend-demo.onrender.com"


def login():
    """Login and return auth headers"""
    phone_number = "+998912223344"
    password = "1"

    print(f"\n--- Logging in (Target: {BASE_URL}) ---")
    login_url = f"{BASE_URL}/auth/web/login/"
    try:
        res = requests.post(login_url, json={
            "phone_number": phone_number,
            "password": password
        })
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return None

    if res.status_code != 200:
        print(f"❌ Login failed: {res.status_code}")
        try:
            pprint(res.json())
        except:
            print(res.text[:500])
        return None

    tokens = res.json()
    access_token = tokens.get("access") or tokens.get("access_token")
    if not access_token:
        print("❌ Could not find access token in response.")
        pprint(tokens)
        return None

    print(f"✅ Login successful.")
    return {"Authorization": f"Bearer {access_token}"}


def test_excavator_suborder_start(auth_headers):
    """Test ExcavatorSubOrder start endpoint with files"""
    print("\n" + "="*60)
    print("TESTING: ExcavatorSubOrder START endpoint with files")
    print("="*60)

    # First, get list of excavator sub-orders
    print("\n1. Fetching excavator sub-orders...")
    list_url = f"{BASE_URL}/excavator-order/sub-orders/"
    res = requests.get(list_url, headers=auth_headers)

    if res.status_code != 200:
        print(f"❌ Failed to fetch sub-orders: {res.status_code}")
        return False

    data = res.json()
    results = data.get('results', [])

    if not results:
        print("❌ No sub-orders found to test")
        return False

    # Find a sub-order with NEW status
    target_suborder = None
    for sub in results:
        if sub.get('status') == 'NEW':
            target_suborder = sub
            break

    if not target_suborder:
        print("❌ No sub-order with NEW status found. Using first available.")
        target_suborder = results[0]

    sub_order_id = target_suborder['id']
    print(f"✅ Using sub-order ID: {sub_order_id}")
    print(f"   Current status: {target_suborder.get('status')}")
    print(f"   before_files count: {len(target_suborder.get('before_files', []))}")
    print(f"   after_files count: {len(target_suborder.get('after_files', []))}")

    # Call start endpoint (without files for now)
    print(f"\n2. Calling START endpoint...")
    start_url = f"{BASE_URL}/excavator-order/sub-orders/{sub_order_id}/start/"

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    print(f"   URL: {start_url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    res = requests.post(start_url, headers=auth_headers, json=payload)

    print(f"\n   Status Code: {res.status_code}")
    if res.status_code == 200:
        try:
            response_data = res.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response (first 500 chars): {res.text[:500]}")
    else:
        print(f"   ❌ Error response (first 1000 chars): {res.text[:1000]}")
        print("❌ START endpoint failed")
        return False

    print("✅ START endpoint succeeded")

    # Verify files were saved
    print(f"\n3. Verifying files were saved...")
    verify_url = f"{BASE_URL}/excavator-order/sub-orders/{sub_order_id}/"
    res = requests.get(verify_url, headers=auth_headers)

    if res.status_code != 200:
        print(f"❌ Failed to verify: {res.status_code}")
        return False

    verified_data = res.json()
    before_files = verified_data.get('before_files', [])
    after_files = verified_data.get('after_files', [])

    print(f"   Status after start: {verified_data.get('status')}")
    print(f"   before_files count: {len(before_files)}")
    print(f"   after_files count: {len(after_files)}")

    if len(before_files) > 0:
        print(f"   ✅ Files saved successfully!")
        print(f"   before_files: {before_files}")
        return True
    else:
        print(f"   ❌ Files were NOT saved!")
        return False


def test_excavator_suborder_finish(auth_headers):
    """Test ExcavatorSubOrder finish endpoint with files"""
    print("\n" + "="*60)
    print("TESTING: ExcavatorSubOrder FINISH endpoint with files")
    print("="*60)

    # First, get list of excavator sub-orders
    print("\n1. Fetching excavator sub-orders...")
    list_url = f"{BASE_URL}/excavator-order/sub-orders/"
    res = requests.get(list_url, headers=auth_headers)

    if res.status_code != 200:
        print(f"❌ Failed to fetch sub-orders: {res.status_code}")
        return False

    data = res.json()
    results = data.get('results', [])

    if not results:
        print("❌ No sub-orders found to test")
        return False

    # Find a sub-order with IN_PROGRESS status
    target_suborder = None
    for sub in results:
        if sub.get('status') == 'IN_PROGRESS':
            target_suborder = sub
            break

    if not target_suborder:
        print("❌ No sub-order with IN_PROGRESS status found. Using first available.")
        target_suborder = results[0]

    sub_order_id = target_suborder['id']
    print(f"✅ Using sub-order ID: {sub_order_id}")
    print(f"   Current status: {target_suborder.get('status')}")
    print(f"   before_files count: {len(target_suborder.get('before_files', []))}")
    print(f"   after_files count: {len(target_suborder.get('after_files', []))}")

    # Call finish endpoint (without files for now)
    print(f"\n2. Calling FINISH endpoint...")
    finish_url = f"{BASE_URL}/excavator-order/sub-orders/{sub_order_id}/finish/"

    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    print(f"   URL: {finish_url}")
    print(f"   Payload: {json.dumps(payload, indent=2)}")

    res = requests.post(finish_url, headers=auth_headers, json=payload)

    print(f"\n   Status Code: {res.status_code}")
    if res.status_code == 200:
        try:
            response_data = res.json()
            print(f"   Response: {json.dumps(response_data, indent=2)}")
        except:
            print(f"   Response (first 500 chars): {res.text[:500]}")
    else:
        print(f"   ❌ Error response (first 1000 chars): {res.text[:1000]}")
        print("❌ FINISH endpoint failed")
        return False

    print("✅ FINISH endpoint succeeded")

    # Verify files were saved
    print(f"\n3. Verifying files were saved...")
    verify_url = f"{BASE_URL}/excavator-order/sub-orders/{sub_order_id}/"
    res = requests.get(verify_url, headers=auth_headers)

    if res.status_code != 200:
        print(f"❌ Failed to verify: {res.status_code}")
        return False

    verified_data = res.json()
    before_files = verified_data.get('before_files', [])
    after_files = verified_data.get('after_files', [])

    print(f"   Status after finish: {verified_data.get('status')}")
    print(f"   before_files count: {len(before_files)}")
    print(f"   after_files count: {len(after_files)}")

    if len(after_files) > 0:
        print(f"   ✅ Files saved successfully!")
        print(f"   after_files: {after_files}")
        return True
    else:
        print(f"   ❌ Files were NOT saved!")
        return False


def run_tests():
    auth_headers = login()
    if not auth_headers:
        return

    print("\n" + "="*60)
    print("SELECT TEST TO RUN:")
    print("1. Test START endpoint (with files)")
    print("2. Test FINISH endpoint (with files)")
    print("3. Run both tests")
    print("="*60)

    choice = input("\nSelect option (1-3): ").strip()

    if choice == "1":
        test_excavator_suborder_start(auth_headers)
    elif choice == "2":
        test_excavator_suborder_finish(auth_headers)
    elif choice == "3":
        start_ok = test_excavator_suborder_start(auth_headers)
        finish_ok = test_excavator_suborder_finish(auth_headers)

        print("\n" + "="*60)
        print("SUMMARY:")
        print(f"   START test: {'✅ PASSED' if start_ok else '❌ FAILED'}")
        print(f"   FINISH test: {'✅ PASSED' if finish_ok else '❌ FAILED'}")
        print("="*60)
    else:
        print("Invalid option")


if __name__ == "__main__":
    run_tests()
