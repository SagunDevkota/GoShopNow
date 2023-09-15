"""
Serializers for product model.
"""
from rest_framework import serializers

from core.models import Product,ProductImage
from core.documents import ProductDocument

from review.serializers import ReviewSerializer

from typing import Optional

from django_elasticsearch_dsl_drf.serializers import DocumentSerializer

class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images."""

    class Meta:
        model = ProductImage
        fields = ['image_url']
        read_only_fields = ['image_url']

class ProductSerializer(serializers.ModelSerializer):
    """Serializer for product"""

    def get_first_image_url(self, product):
        first_image = product.product_id_image.first()
        if first_image:
            return first_image.image_url.url
        return None
    
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['p_id', 'name', 'price', 'rating', 'category', 'image_url']
        read_only_fields = ['rating', 'p_id']

    def get_image_url(self, product) -> Optional[str]:
        return self.get_first_image_url(product)
    
class ProductDocumentSerializer(DocumentSerializer):
    """Document serializer for elasticsearch of product"""

    class Meta:
        model = Product
        document = ProductDocument
        fields = ['p_id', 'name', 'price', 'rating', 'category','image_url']
        read_only_fields = ['rating', 'p_id']


class ProductDetailSerializer(serializers.ModelSerializer):
    """Serializer for product including description."""
    review = ReviewSerializer(many=True, read_only=True, source='product_id_review')
    image_url = ProductImageSerializer(many=True, read_only=True, source='product_id_image')
    class Meta:
        model = Product
        fields = ['p_id', 'name', 'price', 'threshold', 'stock', 'rating', 'description', 'review', 'category','image_url']
        read_only_fields = ['rating','id']
