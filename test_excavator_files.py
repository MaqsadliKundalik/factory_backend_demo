#!/usr/bin/env python3
"""Test script for ExcavatorSubOrder start/finish file upload"""

import requests
import json
import sys
from datetime import datetime, timezone

# Configuration
BASE_URL = "https://factory-backend-demo.onrender.com"
TOKEN = "YOUR_JWT_TOKEN_HERE"  # Replace with actual token
SUB_ORDER_ID = "YOUR_SUB_ORDER_ID_HERE"  # Replace with actual sub-order ID

# Test file UUIDs (replace with actual file UUIDs from your system)
TEST_FILE_IDS = [
    "550e8400-e29b-41d4-a716-446655440000",  # Replace with actual file UUID
]

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}


def test_start_endpoint():
    """Test the start endpoint with files"""
    url = f"{BASE_URL}/api/excavator/sub-orders/{SUB_ORDER_ID}/start/"
    
    payload = {
        "files": TEST_FILE_IDS,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"Testing START endpoint")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def test_finish_endpoint():
    """Test the finish endpoint with files"""
    url = f"{BASE_URL}/api/excavator/sub-orders/{SUB_ORDER_ID}/finish/"
    
    payload = {
        "files": TEST_FILE_IDS,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    print(f"\n{'='*60}")
    print(f"Testing FINISH endpoint")
    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


def verify_files_saved():
    """Verify that files were saved by fetching the sub-order"""
    url = f"{BASE_URL}/api/excavator/sub-orders/{SUB_ORDER_ID}/"
    
    print(f"\n{'='*60}")
    print(f"Verifying files saved - GET sub-order")
    print(f"URL: {url}")
    print(f"{'='*60}\n")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        data = response.json()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(data, indent=2)}")
        
        # Check if files are in the response
        before_files = data.get("before_files", [])
        after_files = data.get("after_files", [])
        
        print(f"\n{'='*60}")
        print(f"VERIFICATION RESULT:")
        print(f"before_files count: {len(before_files)}")
        print(f"after_files count: {len(after_files)}")
        
        if before_files:
            print(f"before_files: {before_files}")
        if after_files:
            print(f"after_files: {after_files}")
        print(f"{'='*60}\n")
        
        return len(before_files) > 0 or len(after_files) > 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def main():
    print("\n" + "="*60)
    print("EXCAVATOR SUB-ORDER FILE UPLOAD TEST")
    print("="*60)
    
    # Check if token and ID are set
    if TOKEN == "YOUR_JWT_TOKEN_HERE":
        print("\n[ERROR] Please set your JWT TOKEN in the script!")
        sys.exit(1)
    
    if SUB_ORDER_ID == "YOUR_SUB_ORDER_ID_HERE":
        print("\n[ERROR] Please set your SUB_ORDER_ID in the script!")
        sys.exit(1)
    
    # Run tests
    print("\n1. Testing START endpoint...")
    start_ok = test_start_endpoint()
    
    print("\n2. Verifying after START...")
    verify_files_saved()
    
    # Uncomment to test finish (only if sub-order is in progress)
    # print("\n3. Testing FINISH endpoint...")
    # finish_ok = test_finish_endpoint()
    # 
    # print("\n4. Verifying after FINISH...")
    # verify_files_saved()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
