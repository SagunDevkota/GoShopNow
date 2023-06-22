"""
Serializers for cart model.
"""
from rest_framework import serializers

from core.models import Cart

class CartSerializer(serializers.ModelSerializer):
    """Serializer for cart."""

    class Meta:
        model = Cart
        fields = ['id', 'p_id', 'quantity', 'user']
        read_only_fields = ['user']

    def create(self, validated_data):
        user = self.context['request'].user
        product = validated_data.get('p_id')
        cart = Cart.objects.filter(p_id=product, user=user).first()

        if cart:
            cart.quantity += validated_data['quantity']
            if(cart.quantity > product.stock):
                raise serializers.ValidationError({'error': 'Not Enough Stock'})
            cart.save()
            return cart
        if product and validated_data['quantity'] > product.stock:
            raise serializers.ValidationError({'error': 'Not Enough Stock'})

        return super().create(validated_data)