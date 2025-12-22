from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, CartItem
from .serializers import CartSerializer
from catlog.models import Product

class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    # GET /cart/
    def list(self, request):
        user = request.user

        if user.role != 'customer':
            return Response(
                {"detail": "Only customers can have a cart."},
                status=status.HTTP_403_FORBIDDEN
            )

        cart, _ = Cart.objects.get_or_create(user=user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    # POST /cart/add/
    @action(detail=False, methods=['post'], url_path='add')
    def add(self, request):
        user = request.user

        if user.role != 'customer':
            return Response(
                {"detail": "Only customers can add items to cart."},
                status=status.HTTP_403_FORBIDDEN
            )

        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response(
                {"product_id": "This field is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response(
                {"detail": "Product not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if product.stock < quantity:
            return Response(
                {"detail": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, _ = Cart.objects.get_or_create(user=user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if created:
            cart_item.quantity = quantity
        else:
            cart_item.quantity += quantity

        cart_item.save()

        return Response(
            {"message": "Product added to cart successfully."},
            status=status.HTTP_200_OK
        )

    # PUT /cart/item/<id>/
    @action(detail=True, methods=['put'], url_path='item')
    def update_item(self, request, pk=None):
        quantity = int(request.data.get('quantity', 1))

        try:
            cart_item = CartItem.objects.get(
                id=pk,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if cart_item.product.stock < quantity:
            return Response(
                {"detail": "Not enough stock available."},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        return Response({"message": "Cart updated successfully."})

    # DELETE /cart/item/<id>/
    @action(detail=True, methods=['delete'], url_path='item')
    def remove_item(self, request, pk=None):
        try:
            cart_item = CartItem.objects.get(
                id=pk,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {"detail": "Cart item not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        return Response(
            {"message": "Item removed from cart."},
            status=status.HTTP_204_NO_CONTENT
        )
