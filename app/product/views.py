"""View for product model"""

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from product import serializers
from core.pagination import CustomPagination
from core.models import Product,Cart,Review
    
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
    
class CartViewSet(viewsets.ModelViewSet):
    """View for cart."""
    serializer_class = serializers.CartSerializer
    queryset = Cart.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-id")

class ReviewViewSet(viewsets.ModelViewSet):
    """View for reviews."""
    serializer_class = serializers.ReviewSerializer
    queryset = Cart.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.order_by("-id")