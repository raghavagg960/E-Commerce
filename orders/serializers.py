from rest_framework import serializers
from .models import Order, OrderItem
from users.models import Address
from users.serializers import AddressSerializer


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
    shipping_address = AddressSerializer(read_only=True)
    address_id = serializers.PrimaryKeyRelatedField(
        queryset=Address.objects.all(), source='shipping_address', write_only=True, required=False
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'total_amount',
            'status',
            'shipping_address',
            'address_id',
            'created_at',
            'items',
        ]
        read_only_fields = ['total_amount', 'status', 'created_at']

    def validate_address_id(self, value):
        user = self.context['request'].user
        if value and value.user != user:
            raise serializers.ValidationError("This address does not belong to you.")
        return value
