from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    vendor_name = serializers.CharField(source='vendor.shop_name', read_only=True)

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product_name',
            'vendor_name',
            'quantity',
            'price',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'total_amount',
            'status',
            'created_at',
            'items',
        ]
