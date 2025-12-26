import os
import django
import sys
from decimal import Decimal

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')

try:
    django.setup()
except Exception as e:
    print(f"Setup Error: {e}")
    sys.exit(1)

from rest_framework.test import APIRequestFactory, force_authenticate
from users.models import User, VendorProfile, Address
from orders.models import Order
from payments.views import PaymentViewSet
from payments.models import Payment

def run_verification():
    print("Setting up test data for Payment...")
    
    # Create or get a customer
    customer_email = "test_payment_user@example.com"
    customer, _ = User.objects.get_or_create(email=customer_email, defaults={
        'first_name': 'Pay',
        'last_name': 'User', 
        'role': 'customer',
        'mobile_no': '5555566666'
    })

    # Create dummy address
    address, _ = Address.objects.get_or_create(user=customer, defaults={
        'street_address': 'Payment St',
        'city': 'Pay City',
        'state': 'PS',
        'postal_code': '99999',
        'country': 'PayLand'
    })

    # Create dummy Order (pending)
    order = Order.objects.create(
        user=customer,
        shipping_address=address,
        total_amount=Decimal('500.00'),
        status='pending'
    )
    print(f"Created Pending Order #{order.id} with amount 500.00")

    # TEST: Make Payment
    print("\nTesting PaymentViewSet create action...")
    factory = APIRequestFactory()
    
    # payload
    data = {
        "order_id": order.id,
        "amount": 500.00
    }
    
    request = factory.post('/payments/', data, format='json')
    force_authenticate(request, user=customer)
    
    view = PaymentViewSet.as_view({'post': 'create'})
    response = view(request)
    
    print(f"Response Status Code: {response.status_code}")
    print("Response Data:")
    print(response.data)

    # Verify Database
    order.refresh_from_db()
    print(f"\nOrder Status after payment: {order.status}")

    if response.status_code == 201 and order.status == 'confirmed':
        print("\nSUCCESS: Payment successful and Order confirmed.")
    else:
        print("\nFAILURE: Payment flow failed.")

if __name__ == "__main__":
    try:
        run_verification()
    except Exception as e:
        print(f"An error occurred: {e}")
