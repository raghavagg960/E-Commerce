import os
import django
from decimal import Decimal

# Setup Django
import sys
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
print(f"DJANGO_SETTINGS_MODULE: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
print(f"CWD: {os.getcwd()}")
print(f"Sys Path: {sys.path}")

try:
    django.setup()
except Exception as e:
    print(f"Setup Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import User, VendorProfile, Address
from orders.models import Order, OrderItem
from catlog.models import Product, Category
from orders.views import OrderViewSet

def run_verification():
    print("Setting up test data...")
    
    # Create or get a customer
    customer_email = "test_customer_verify@example.com"
    customer, _ = User.objects.get_or_create(email=customer_email, defaults={
        'first_name': 'Test',
        'last_name': 'Customer', 
        'role': 'customer',
        'mobile_no': '9876554321'
    })

    # Create or get a vendor
    vendor_email = "test_vendor_verify@example.com"
    vendor_user, _ = User.objects.get_or_create(email=vendor_email, defaults={
        'first_name': 'Test',
        'last_name': 'Vendor',
        'role': 'vendor'
    })
    vendor_profile, _ = VendorProfile.objects.get_or_create(user=vendor_user, defaults={
        'shop_name': 'Test Shop'
    })

    # Create dummy product
    category, _ = Category.objects.get_or_create(name="Test Category", defaults={'slug': 'test-category'})
    product, _ = Product.objects.get_or_create(name="Test Product", defaults={
        'vendor': vendor_profile,
        'category': category,
        'description': 'Desc',
        'price': Decimal('100.00'),
        'stock': 10
    })

    # Create address
    address, _ = Address.objects.get_or_create(user=customer, defaults={
        'street_address': '123 Test St',
        'city': 'Test City',
        'state': 'TS',
        'postal_code': '12345',
        'country': 'TestLand'
    })

    # Create Order
    order = Order.objects.create(
        user=customer,
        shipping_address=address,
        total_amount=Decimal('200.00'),
        status='pending'
    )
    
    # Create Order Item
    OrderItem.objects.create(
        order=order,
        product=product,
        vendor=vendor_profile,
        quantity=2,
        price=Decimal('100.00')
    )

    print(f"Created Order #{order.id} for user {customer.email}")

    # Test Retrieve View
    print("\nTesting OrderViewSet retrieve action...")
    factory = APIRequestFactory()
    request = factory.get(f'/orders/{order.id}/')
    force_authenticate(request, user=customer)
    
    view = OrderViewSet.as_view({'get': 'retrieve'})
    response = view(request, pk=order.id)
    
    print(f"Response Status Code: {response.status_code}")
    print("Response Data:")
    print(response.data)

    if response.status_code == 200 and response.data['id'] == order.id:
        print("\nSUCCESS: Order retrieved successfully.")
    else:
        print("\nFAILURE: Could not retrieve order.")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"An error occurred: {e}")
