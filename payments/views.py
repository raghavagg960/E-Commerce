from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
import uuid

from .models import Payment
from .serializers import PaymentSerializer
from orders.models import Order

class PaymentViewSet(viewsets.GenericViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def create(self, request):
        user = request.user
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')

        if not order_id or not amount:
            return Response(
                {"detail": "Order ID and Amount are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Verify order belongs to user
            order = Order.objects.get(id=order_id, user=user)
        except Order.DoesNotExist:
            return Response(
                {"detail": "Invalid Order ID."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if already paid
        if order.status in ['confirmed', 'shipped', 'delivered']: # Assuming 'confirmed' means paid for now
            return Response(
                {"detail": "Order is already paid/confirmed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify amount (casting to float/decimal for comparison)
        try:
            amount_float = float(amount)
            if abs(float(order.total_amount) - amount_float) > 0.01:
                 return Response(
                    {"detail": "Incorrect amount."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
             return Response(
                {"detail": "Invalid amount format."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # MOCK PAYMENT SUCCESS
        transaction_id = f"MOCK-{uuid.uuid4().hex[:10].upper()}"
        
        payment = Payment.objects.create(
            order=order,
            user=user,
            transaction_id=transaction_id,
            amount=order.total_amount,
            status='completed',
            payment_method='mock_card'
        )

        # Update Order Status
        order.status = 'confirmed'
        order.save()

        serializer = self.get_serializer(payment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
