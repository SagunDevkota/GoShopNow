from rest_framework import serializers
from core.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment model."""
    class Meta:
        model = Payment
        fields = ["id","quantity","status","transaction_id","date_time","amount"]

class CreatePaymentSerializer(serializers.ModelSerializer):
    """Serializer for initiating payment."""
    coupon_code = serializers.CharField()
    class Meta:
        model = Payment
        fields = ["date_time","coupon_code"]
        read_only_fields = ["date_time"]