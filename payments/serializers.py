from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Payment
        fields = [
            'id',
            'order_id',
            'transaction_id',
            'amount',
            'status',
            'payment_method',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'transaction_id',
            'status',
            'created_at',
            'payment_method'
        ]
