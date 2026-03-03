import requests
import json
import uuid
import time

BASE_URL = "http://localhost:8002"
ADMIN_PHONE = "+998912223344"
ADMIN_PASSWORD = "admin123"

def print_result(msg, success=True):
    prefix = "✓" if success else "✗"
    print(f"{prefix} {msg}")

class TestRunner:
    def __init__(self):
        self.admin_token = None
        self.operator_token = None
        self.operator_id = None
        self.whouse_id = None
        self.pt_id = None
        self.pu_id = None
        self.p_id = None

    def login(self, phone, password):
        url = f"{BASE_URL}/auth/web/login/"
        resp = requests.post(url, json={
            "phone_number": phone,
            "password": password,
            "platform": "web"
        })
        if resp.status_code == 200:
            return resp.json()["access_token"]
        return None

    def run(self):
        print(f"--- Starting Comprehensive System Test at {BASE_URL} ---")

        # 1. ADMIN LOGIN
        self.admin_token = self.login(ADMIN_PHONE, ADMIN_PASSWORD)
        if not self.admin_token:
            print_result("Admin login failed", False)
            return
        print_result("Admin login successful")
        admin_headers = {"Authorization": f"Bearer {self.admin_token}"}

        # 2. GET WAREHOUSE
        resp = requests.get(f"{BASE_URL}/whouse/", headers=admin_headers)
        if resp.status_code == 200 and len(resp.json()) > 0:
            self.whouse_id = resp.json()[0]["id"]
            print_result(f"Found default warehouse: {self.whouse_id}")
        else:
            print_result("Failed to find warehouse", False)
            return

        # 3. CREATE OPERATOR
        # Use a unique phone number for each run to be safe, but also cleanup
        unique_suffix = str(int(time.time()))[-6:]
        op_phone = f"+99890{unique_suffix}0"
        
        # Cleanup if exists (using our new endpoint)
        requests.delete(f"{BASE_URL}/users/delete_by_phone/", headers=admin_headers, json={"phone": op_phone})
        
        op_data = {
            "name": "Test Operator",
            "phone_number": op_phone,
            "password": "operator123",
            "role": "operator",
            "whouse": self.whouse_id,
            "crud_product": True,
            "crud_client": True,
            "crud_transport": True,
            "read_whouse": True
        }
        resp = requests.post(f"{BASE_URL}/users/", headers=admin_headers, json=op_data)
        if resp.status_code == 201:
            self.operator_id = resp.json()["id"]
            print_result(f"Created Test Operator: {op_phone}")
        else:
            print_result(f"Failed to create operator: {resp.status_code} {resp.text}", False)
            return

        # 4. OPERATOR LOGIN
        self.operator_token = self.login(op_phone, "operator123")
        if not self.operator_token:
            print_result("Operator login failed", False)
            return
        print_result("Operator login successful")
        op_headers = {"Authorization": f"Bearer {self.operator_token}"}

        # 5. PRODUCT CRUD (as Operator)
        # Create Type
        resp = requests.post(f"{BASE_URL}/products/types/", headers=op_headers, json={"name": f"Test Type {unique_suffix}"})
        if resp.status_code == 201:
            self.pt_id = resp.json()["id"]
            print_result("Product Type creation successful")
        else:
            print_result(f"Product Type creation failed: {resp.text}", False)
        
        # Create Unit
        resp = requests.post(f"{BASE_URL}/products/units/", headers=op_headers, json={"name": f"Unit {unique_suffix}"})
        if resp.status_code == 201:
            self.pu_id = resp.json()["id"]
            print_result("Product Unit creation successful")

        # Create Product
        resp = requests.post(f"{BASE_URL}/products/", headers=op_headers, json={
            "name": f"Product {unique_suffix}",
            "types": [self.pt_id] if self.pt_id else [],
            "unit": self.pu_id
        })
        if resp.status_code == 201:
            self.p_id = resp.json()["id"]
            print_result("Product item creation successful")
        else:
            print_result(f"Product item creation failed: {resp.text}", False)

        # 6. CLIENT CRUD
        resp = requests.post(f"{BASE_URL}/clients/", headers=op_headers, json={
            "name": f"Client {unique_suffix}",
            "inn_number": unique_suffix,
            "phone_number": f"+9989{unique_suffix}1",
            "latitude": "41.0",
            "longitude": "69.0"
        })
        if resp.status_code == 201:
            print_result("Client creation successful")
        else:
            print_result(f"Client creation failed: {resp.text}", False)

        # 7. NEGATIVE PERMISSION TEST
        print("Testing permission restriction...")
        # Strip client permission from operator
        resp = requests.patch(f"{BASE_URL}/users/{self.operator_id}/", headers=admin_headers, json={"crud_client": False})
        if resp.status_code != 200:
            print_result("Failed to update operator permissions", False)
        
        # Try to create client again as operator -> should fail
        resp = requests.post(f"{BASE_URL}/clients/", headers=op_headers, json={
            "name": "Should Fail",
            "inn_number": "00000",
            "phone_number": "+00000",
            "latitude": "0",
            "longitude": "0"
        })
        if resp.status_code == 403:
            print_result("Permission restriction verified (403 Forbidden as expected)")
        else:
            print_result(f"Permission restriction FAILED: Expected 403, got {resp.status_code} {resp.text}", False)

        print("--- Comprehensive Test Completed ---")

if __name__ == "__main__":
    TestRunner().run()
