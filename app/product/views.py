"""View for product model"""

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from product import serializers
from core.models import Product,Cart
    
class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
    ):
    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.all()

    def get_serializer_class(self):
        if(self.action == 'retrieve'):
            return serializers.ProductDetailSerializer
        return self.serializer_class
    
class CartViewSet(viewsets.ModelViewSet):
    """View for cart."""
    serializer_class = serializers.CartSerializer
    queryset = Cart.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)