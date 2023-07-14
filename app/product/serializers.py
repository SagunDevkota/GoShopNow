"""
Serializers for product model.
"""
from rest_framework import serializers

from core.models import Product

from review.serializers import ReviewSerializer


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
