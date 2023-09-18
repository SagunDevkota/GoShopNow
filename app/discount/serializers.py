from rest_framework.serializers import ModelSerializer

from core.models import DiscountCoupon

class DiscountCouponSerializer(ModelSerializer):
    """Serializer for discount coupon model."""
    class Meta:
        model = DiscountCoupon
        fields = ['coupon_code','max_amount','max_percentage']