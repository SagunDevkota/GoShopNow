"""
Serializer for address model.
"""
from rest_framework import serializers
from core.models import Address,DeliveryAddress

class AddressSerializer(serializers.ModelSerializer):
    """Serializer for address model"""
    class Meta:
        model = Address
        fields = ['id','name']
        read_only_fields = ['id','name']

class DeliveryAddressSerializer(serializers.ModelSerializer):
    """Serializer for delivery address model."""
    class Meta:
        model = DeliveryAddress
        fields = ['provience','city','area']