"""View for cart model"""

from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from cart import serializers
from core.pagination import CustomPagination
from core.models import Cart

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