#!/usr/bin/env python3
"""Test script for ExcavatorSubOrder start/finish file upload"""

import requests
import json
import sys
import os
from datetime import datetime, timezone

# Configuration - can be set via environment variables or hardcoded
BASE_URL = os.getenv("API_URL", "https://factory-backend-demo.onrender.com")
TOKEN = os.getenv("JWT_TOKEN", "")
SUB_ORDER_ID = os.getenv("SUB_ORDER_ID", "")

# Test file UUIDs (replace with actual file UUIDs from your system)
TEST_FILE_IDS = [
    "550e8400-e29b-41d4-a716-446655440000",  # Replace with actual file UUID
]


def get_auth_token():
    """Get token via login if not provided"""
    phone = input("Enter phone number: ")
    password = input("Enter password: ")
    
    url = f"{BASE_URL}/api/common/auth/login/"
    payload = {"phone": phone, "password": password}
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        if response.status_code == 200:
            token = data.get("access") or data.get("token")
            print(f"\n[OK] Login successful!")
            print(f"Token: {token[:50]}...")
            return token
        else:
            print(f"[ERROR] Login failed: {data}")
            return None
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def test_start_endpoint(token, sub_order_id, file_ids=None):
    """Test the start endpoint with files"""
    url = f"{BASE_URL}/api/excavator/sub-orders/{sub_order_id}/start/"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "files": file_ids or TEST_FILE_IDS,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"Testing START endpoint")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def test_finish_endpoint(token, sub_order_id, file_ids=None):
    """Test the finish endpoint with files"""
    url = f"{BASE_URL}/api/excavator/sub-orders/{sub_order_id}/finish/"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "files": file_ids or TEST_FILE_IDS,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"Testing FINISH endpoint")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")
        return response.status_code == 200
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def verify_suborder(token, sub_order_id):
    """Verify that files were saved by fetching the sub-order"""
    url = f"{BASE_URL}/api/excavator/sub-orders/{sub_order_id}/"
    
    headers = {"Authorization": f"Bearer {token}"}
    
    print(f"\n{'='*60}")
    print(f"Fetching sub-order to verify files")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        before_files = data.get("before_files", [])
        after_files = data.get("after_files", [])
        
        print(f"\n{'='*60}")
        print(f"VERIFICATION:")
        print(f"before_files count: {len(before_files)}")
        print(f"after_files count: {len(after_files)}")
        print(f"status: {data.get('status')}")
        print(f"{'='*60}\n")
        
        return data
    except Exception as e:
        print(f"[ERROR] {e}")
        return None


def main():
    print("\n" + "="*60)
    print("EXCAVATOR SUB-ORDER FILE UPLOAD TEST")
    print("="*60)
    
    # Get token
    token = TOKEN
    if not token:
        print("\nNo JWT_TOKEN set. Please login:")
        token = get_auth_token()
        if not token:
            sys.exit(1)
    
    # Get sub-order ID
    sub_order_id = SUB_ORDER_ID
    if not sub_order_id:
        sub_order_id = input("\nEnter sub-order ID: ").strip()
        if not sub_order_id:
            print("[ERROR] Sub-order ID is required!")
            sys.exit(1)
    
    # Menu
    print("\n" + "="*60)
    print("OPTIONS:")
    print("1. Test START endpoint (with files)")
    print("2. Test FINISH endpoint (with files)")
    print("3. Verify sub-order (GET request)")
    print("4. Run all tests")
    print("="*60)
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        test_start_endpoint(token, sub_order_id)
        verify_suborder(token, sub_order_id)
    elif choice == "2":
        test_finish_endpoint(token, sub_order_id)
        verify_suborder(token, sub_order_id)
    elif choice == "3":
        verify_suborder(token, sub_order_id)
    elif choice == "4":
        test_start_endpoint(token, sub_order_id)
        verify_suborder(token, sub_order_id)
        test_finish_endpoint(token, sub_order_id)
        verify_suborder(token, sub_order_id)
    else:
        print("[ERROR] Invalid option!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
