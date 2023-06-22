"""View for product model"""

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from product import serializers
from core.pagination import CustomPagination
from core.models import Product,Review
    
class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
    ):
    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.all()
    pagination_class = CustomPagination

    def get_serializer_class(self):
        if(self.action == 'retrieve'):
            return serializers.ProductDetailSerializer
        return self.serializer_class
    
    def get_queryset(self):
        return self.queryset.order_by("-p_id")