from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction

from .models import Order, OrderItem
from .serializers import OrderSerializer
from cart.models import Cart

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Default queryset:
        - customers see their own orders
        - vendors don't use this (they use vendor_orders action)
        """
        user = self.request.user
        if user.role == 'customer':
            return Order.objects.filter(user=user).order_by('-created_at')
        return Order.objects.none()

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        user = request.user

        if user.role != 'customer':
            return Response(
                {"detail": "Only customers can place orders."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not cart.items.exists():
            return Response(
                {"detail": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = 0
        order_items_data = []

        # Validate stock + calculate total
        for item in cart.items.all():
            product = item.product

            if product.stock < item.quantity:
                return Response(
                    {"detail": f"Not enough stock for {product.name}."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            price = product.discount_price or product.price
            total_amount += price * item.quantity

            order_items_data.append({
                "product": product,
                "vendor": product.vendor,
                "quantity": item.quantity,
                "price": price,
            })

        # Create order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount
        )

        # Create order items + reduce stock
        for data in order_items_data:
            OrderItem.objects.create(order=order, **data)
            data["product"].stock -= data["quantity"]
            data["product"].save()

        # Clear cart
        cart.items.all().delete()

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='my')
    def my_orders(self, request):
        orders = Order.objects.filter(
            user=request.user
        ).order_by('-created_at')

        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='vendor')
    def vendor_orders(self, request):
        user = request.user

        if user.role != 'vendor':
            return Response(
                {"detail": "Only vendors can access this."},
                status=status.HTTP_403_FORBIDDEN
            )

        vendor = user.vendor_profile

        items = OrderItem.objects.filter(
            vendor=vendor
        ).select_related('order', 'product').order_by('-order__created_at')

        data = []
        for item in items:
            data.append({
                "order_id": item.order.id,
                "product": item.product.name,
                "quantity": item.quantity,
                "price": item.price,
                "status": item.order.status,
                "ordered_at": item.order.created_at,
            })

        return Response(data)

