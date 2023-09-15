"""View for review model"""
from django.db.models import Avg

from rest_framework import viewsets,mixins
from rest_framework.validators import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import extend_schema
from review import serializers
from core.pagination import CustomPagination
from core.models import Review,Payment,Product,PaymentProduct

class ReviewViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,
                    mixins.DestroyModelMixin):
    """View for reviews."""
    serializer_class = serializers.ReviewSerializer
    queryset = Review.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = CustomPagination

    def get_queryset(self):
        if(self.action=='list'):
            if ('p_id' not in self.request.query_params.keys()):
                raise ValidationError({"error":["p_id not provided."]})
            
            product_id = self.request.query_params.get('p_id')
            return self.queryset.filter(p_id=product_id).order_by("-id")
        return self.queryset
    
    def perform_create(self, serializer):
        data = serializer.validated_data
        # purchase = Payment.objects.filter(product=data["p_id"],user=self.request.user,status="Completed")
        purchase = Payment.objects.filter(user=self.request.user,status="Completed")
        purchased_product = PaymentProduct.objects.filter(payment_id__in=purchase,product=data["p_id"])
        if(len(purchased_product)<1):
            raise ValidationError({"error":["You havenot purchased the product yet."]})
        reviews = Review.objects.filter(p_id=data["p_id"],user=self.request.user)
        if(len(reviews)>0):
            raise ValidationError({"error":["Your review is already registered."]})
        
        serializer.save(user=self.request.user)
        product = Product.objects.get(p_id=data["p_id"].p_id)
        product.rating = Review.objects.aggregate(avg_rating=Avg('rating'))['avg_rating']
        product.save()

    @extend_schema(
        parameters=[
            OpenApiParameter(name='p_id',location=OpenApiParameter.QUERY, description='Product ID', required=False, type=str),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        try:
            review = Review.objects.get(id=kwargs.get('pk'))
        except Review.DoesNotExist:
            raise ValidationError({"error":["Details not found."]})
        if(review.user != self.request.user):
            raise ValidationError({"error":["Invalid Request"]})
        return super().destroy(request, *args, **kwargs)