from rest_framework import serializers
from .models import Cart, CartItem
from catlog.serializers import ProductSerializer  # reuse existing serializer

class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

    def get_total_price(self, obj):
        total = 0
        for item in obj.items.all():
            price = item.product.discount_price or item.product.price
            total += price * item.quantity
        return total
