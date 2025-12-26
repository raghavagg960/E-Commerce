import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def get_auth_token(email, password, role="customer"):
    # 1. Register/Login
    print(f"\n[Auth] Processing user {email} ({role})...")
    register_data = {
        "first_name": "Test",
        "last_name": role.capitalize(),
        "email": email,
        "mobile_no": "9999999999" if role == "vendor" else "8888888888",
        "password": password,
        "role": role
    }
    
    if role == "vendor":
        register_data["vendor_profile"] = {
            "shop_name": "Test Shop",
            "gst_number": "GST123"
        }

    login_data = {"email": email, "password": password}
    
    # Try login
    response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
    if response.status_code == 200:
        return response.json()['access']
    
    # Register
    print("Registering...")
    response = requests.post(f"{BASE_URL}/users/register/", json=register_data)
    if response.status_code == 201:
        response = requests.post(f"{BASE_URL}/users/login/", data=login_data)
        return response.json()['access']
    else:
        print(f"Registration failed: {response.text}")
        return None

def run_test():
    print("----------------------------------------------------------------------")
    print("Starting Cart Verification Script")
    print("----------------------------------------------------------------------")

    # 1. Setup Vendor & Product
    vendor_token = get_auth_token("vendor@test.com", "password123", "vendor")
    if not vendor_token: return
    vendor_headers = {"Authorization": f"Bearer {vendor_token}"}

    # Create Category
    print("\n[Setup] Ensuring Category 'Electronics'...")
    # List categories to see if it exists
    list_res = requests.get(f"{BASE_URL}/catlog/categories/", headers=vendor_headers)
    cat_id = None
    if list_res.status_code == 200:
        for cat in list_res.json():
            if cat['name'] == "Electronics":
                cat_id = cat['id']
                print(f"Category found: {cat_id}")
                break
    
    if not cat_id:
        print("Creating Category...")
        cat_res = requests.post(f"{BASE_URL}/catlog/categories/", 
                                json={"name": "Electronics", "slug": "electronics"}, 
                                headers=vendor_headers)
        if cat_res.status_code == 201:
            cat_id = cat_res.json()['id']
            print(f"Category created: {cat_id}")
        else:
            print(f"Category creation failed: {cat_res.status_code} {cat_res.text}")
            return

    # Create Product
    print("\n[Setup] Ensuring Product 'Smartphone'...")
    # Check existing products
    list_res = requests.get(f"{BASE_URL}/catlog/products/", headers=vendor_headers)
    prod_id = None
    if list_res.status_code == 200:
         for prod in list_res.json():
             if prod['name'] == "Smartphone":
                 prod_id = prod['id']
                 print(f"Product found: {prod_id}")
                 break

    if not prod_id:
        print("Creating Product...")
        prod_data = {
            "category_id": cat_id,
            "name": "Smartphone",
            "description": "A cool phone",
            "price": "500.00",
            "stock": 100
        }
        prod_res = requests.post(f"{BASE_URL}/catlog/products/", json=prod_data, headers=vendor_headers)
        if prod_res.status_code == 201:
            prod_id = prod_res.json()['id']
            print(f"Product created: {prod_id}")
        else:
            print(f"Product creation failed: {prod_res.status_code} {prod_res.text}")
            return
    print(f"Product ID: {prod_id}")

    # 2. Customer Action
    cust_token = get_auth_token("customer@test.com", "password123", "customer")
    if not cust_token: return
    headers = {"Authorization": f"Bearer {cust_token}"}

    # Add to Cart
    print("\n[Action] Adding to Cart...")
    res = requests.post(f"{BASE_URL}/cart/add/", json={"product_id": prod_id, "quantity": 2}, headers=headers)
    print(f"Add Status: {res.status_code}")
    print(f"Add Response: {res.text}")

    # List Cart
    print("\n[Action] Listing Cart...")
    res = requests.get(f"{BASE_URL}/cart/", headers=headers)
    print(f"List Status: {res.status_code}")
    cart_data = res.json()
    print(json.dumps(cart_data, indent=2))
    
    if 'items' not in cart_data or len(cart_data['items']) == 0:
        print("Cart is empty! Aborting test.")
        return
    
    item_id = cart_data['items'][0]['id']

    # Update Item
    print(f"\n[Action] Updating Item {item_id}...")
    res = requests.put(f"{BASE_URL}/cart/item/{item_id}/", json={"quantity": 5}, headers=headers)
    print(f"Update Status: {res.status_code}")
    
    # Verify Update
    res = requests.get(f"{BASE_URL}/cart/", headers=headers)
    new_qty = res.json()['items'][0]['quantity']
    print(f"New Quantity: {new_qty}")
    if new_qty != 5:
        print("Update failed!")

    # Remove Item
    print(f"\n[Action] Removing Item {item_id}...")
    res = requests.delete(f"{BASE_URL}/cart/item/{item_id}/delete/", headers=headers)
    print(f"Delete Status: {res.status_code}")

    # Verify Empty
    res = requests.get(f"{BASE_URL}/cart/", headers=headers)
    if len(res.json()['items']) == 0:
        print("Cart is now empty. Success.")
    else:
        print("Cart not empty!")

if __name__ == "__main__":
    run_test()
