import requests
import json
import random

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token(email, password, role="customer"):
    print(f"\n[Auth] Processing user {email} ({role})...")
    
    # Try login
    login_data = {"email": email, "password": password}
    response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
    
    if response.status_code == 200:
        return response.json()['access']
    
    # Register if login fails
    print("Registering...")
    register_data = {
        "first_name": "Test",
        "last_name": role.capitalize(),
        "email": email,
        "mobile_no": str(random.randint(7000000000, 9999999999)),
        "password": password,
        "role": role
    }
    
    if role == "vendor":
        register_data["vendor_profile"] = {
            "shop_name": f"Shop {random.randint(1,1000)}",
            "gst_number": f"GST{random.randint(1000,9999)}"
        }

    response = requests.post(f"{BASE_URL}/users/register/", json=register_data)
    if response.status_code == 201:
        response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
        return response.json()['access']
    else:
        print(f"Registration failed: {response.text}")
        return None

def run_test():
    print("----------------------------------------------------------------------")
    print("Starting Order Verification Script")
    print("----------------------------------------------------------------------")

    # 1. Vendor Setup (Get Product)
    vendor_token = get_auth_token("vendor_order@test.com", "password123", "vendor")
    if not vendor_token: return
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}

    # Ensure Category
    print("\n[Setup] Ensuring Category...")
    cat_id = None
    list_res = requests.get(f"{BASE_URL}/catlog/categories/", headers=vendor_headers)
    if list_res.status_code == 200 and len(list_res.json()) > 0:
        cat_id = list_res.json()[0]['id']
        print(f"Using Category ID: {cat_id}")
    else:
        # Create one
        res = requests.post(f"{BASE_URL}/catlog/categories/", 
                            json={"name": "General", "slug": f"general-{random.randint(1000,9999)}"}, 
                            headers=vendor_headers)
        if res.status_code == 201:
            cat_id = res.json()['id']
            print(f"Created Category ID: {cat_id}")
        else:
            print(f"Failed to create category: {res.text}")
            return

    # Ensure Product
    print("\n[Setup] Ensuring Product...")
    prod_id = None
    list_res = requests.get(f"{BASE_URL}/catlog/products/", headers=vendor_headers)
    if list_res.status_code == 200 and len(list_res.json()) > 0:
        prod_id = list_res.json()[0]['id']
        print(f"Using Product ID: {prod_id}")
    else:
        # Create one
        res = requests.post(f"{BASE_URL}/catlog/products/", 
                            json={
                                "category_id": cat_id,
                                "name": "Test Product",
                                "description": "For Orders",
                                "price": "100.00",
                                "stock": 50
                            }, 
                            headers=vendor_headers)
        if res.status_code == 201:
            prod_id = res.json()['id']
            print(f"Created Product ID: {prod_id}")
        else:
            print(f"Failed to create product: {res.text}")
            return


    # 2. Customer Setup
    cust_token = get_auth_token("cust_order@test.com", "password123", "customer")
    if not cust_token: return
    headers = {"Authorization": f"Bearer {cust_token}"}

    # Create Address
    print("\n[Setup] Creating Address...")
    addr_res = requests.post(f"{BASE_URL}/users/addresses/", 
                             json={
                                 "street_address": "456 Test Ave",
                                 "city": "Order City",
                                 "state": "TS",
                                 "postal_code": "500001",
                                 "country": "India"
                             }, 
                             headers=headers)
    if addr_res.status_code == 201:
        addr_id = addr_res.json()['id']
        print(f"Address Created ID: {addr_id}")
    else:
        # Check if limits reached or similar? Or just proceed if we can list?
        # Let's list
        list_addr = requests.get(f"{BASE_URL}/users/addresses/", headers=headers)
        if list_addr.status_code == 200 and len(list_addr.json()) > 0:
            addr_id = list_addr.json()[0]['id']
            print(f"Using existing Address ID: {addr_id}")
        else:
            print(f"Failed to create address: {addr_res.text}")
            return

    # Add to Cart
    print("\n[Action] Adding 2 items to Cart...")
    cart_res = requests.post(f"{BASE_URL}/cart/add/", 
                             json={"product_id": prod_id, "quantity": 2}, 
                             headers=headers)
    if cart_res.status_code != 200:
        print(f"Failed to add to cart: {cart_res.text}")
        return
    print("Added to cart.")

    # 3. Place Order
    print("\n[Action] Placing Order...")
    order_data = {
        "address_id": addr_id
    }
    order_res = requests.post(f"{BASE_URL}/orders/", json=order_data, headers=headers)
    print(f"Order Status: {order_res.status_code}")
    print(f"Order Response: {order_res.text}")

    if order_res.status_code == 201:
        order_json = order_res.json()
        print(f"Order Placed Successfully! ID: {order_json.get('id')}")
        print(f"Total Amount: {order_json.get('total_amount')}")
        
        # Verify Cart Empty
        print("\n[Verification] Checking if Cart is empty...")
        check_cart = requests.get(f"{BASE_URL}/cart/", headers=headers)
        items = check_cart.json().get('items', [])
        if len(items) == 0:
            print("Cart is successfully emptied.")
        else:
            print(f"Warning: Cart still has {len(items)} items.")
    else:
        print("Order placement failed.")

if __name__ == "__main__":
    run_test()
