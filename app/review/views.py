"""View for review model"""

from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from review import serializers
from core.pagination import CustomPagination
from core.models import Review

class ReviewViewSet(viewsets.ModelViewSet):
    """View for reviews."""
    serializer_class = serializers.ReviewSerializer
    queryset = Review.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        return self.queryset.order_by("-id")
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)