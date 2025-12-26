import requests
import json
import sys

BASE_URL = "http://127.0.0.1:8000"

def run_test():
    print("----------------------------------------------------------------------")
    print("Starting Verification Script")
    print("----------------------------------------------------------------------")

    # 1. Register User
    print("\n[1] Registering User...")
    email = "testuser@example.com"
    password = "password123"
    register_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "mobile_no": "1234567890",
        "password": password,
        "role": "customer"
    }
    
    # Try login first in case user exists
    login_data = {"email": email, "password": password}
    try:
        response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
    except requests.exceptions.ConnectionError:
        print("Error: Would not connect to server. Make sure it is running on 127.0.0.1:8000")
        return

    
    if response.status_code == 200:
        print("User already exists, logging in.")
        token = response.json()['access']
    else:
        response = requests.post(f"{BASE_URL}/users/register/", data=register_data)
        if response.status_code == 201:
            print("User registered.")
            # Login
            response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
            token = response.json()['access']
        else:
            print(f"Registration failed: {response.text}")
            return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Add Address
    print("\n[2] Adding Address...")
    address_data = {
        "street_address": "123 Main St",
        "city": "Tech City",
        "state": "TS",
        "postal_code": "500000",
        "country": "India",
        "is_default": True
    }
    response = requests.post(f"{BASE_URL}/users/addresses/", data=address_data, headers=headers)
    if response.status_code == 201:
        address_id = response.json()['id']
        print(f"Address created with ID: {address_id}")
    else:
        print(f"Address creation failed: {response.text}")
        return

    # 3. List Addresses
    print("\n[3] Listing Addresses...")
    response = requests.get(f"{BASE_URL}/users/addresses/", headers=headers)
    if response.status_code == 200:
        print(f"Addresses found: {len(response.json())}")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"Listing failed: {response.text}")
        return

    print("\n[!] To fully verify Order creation with Address, we need products etc.")
    print("[!] Verification of Address API successful.")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Test failed check is server running? Error: {e}")
