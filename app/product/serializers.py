"""
Serializers for product model.
"""
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from core.models import (Product,Review,Cart)

class ReviewSerializer(serializers.ModelSerializer):
    """Serializer for model"""
    name = serializers.SerializerMethodField()
    class Meta:
        model = Review
        fields = ['review','user','name','rating']
    
    def get_name(self, obj):
        return obj.user.first_name

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product"""
    class Meta:
        model = Product
        fields = ['p_id', 'name', 'price', 'rating', 'category']
        read_only_fields = ['rating','id']

class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product including description."""
    review = ReviewSerializer(many=True, read_only=True, source='product_id_review')
    class Meta:
        model = Product
        fields = ['p_id', 'name', 'price', 'threshold', 'stock', 'rating', 'description', 'review', 'category']
        read_only_fields = ['rating','id']

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