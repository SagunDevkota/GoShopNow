"""View for review model"""

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from core.models import DiscountCoupon
from core.pagination import CustomPagination
from discount.serializers import DiscountCouponSerializer


class DiscountCouponViewSet(GenericViewSet,ListModelMixin):
    """Viewset for discount coupon model."""
    serializer_class = DiscountCouponSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    queryset = DiscountCoupon.objects.filter(used=False)

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(user=self.request.user)
        return queryset