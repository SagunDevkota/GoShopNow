from rest_framework import serializers
from core.models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    """Serializer for payment model."""
    class Meta:
        model = Payment
        fields = ["id","quantity","status","transaction_id","date_time","user","amount"]
        read_only_fields = ["user"]

class CreatePaymentSerializer(serializers.ModelSerializer):
    """Serializer for initiating payment."""
    class Meta:
        model = Payment
        fields = ["date_time"]
        read_only_fields = ["date_time"]