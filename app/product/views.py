"""View for product model"""

from rest_framework import viewsets
from rest_framework import mixins
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import extend_schema

from product import serializers
from core.pagination import CustomPagination
from core.models import Product,Review
    
class ProductViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
    ):
    serializer_class = serializers.ProductSerializer
    queryset = Product.objects.order_by('-p_id')
    pagination_class = CustomPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(name='price',location=OpenApiParameter.QUERY, description='1=asc,0=default,-1=des', required=False, type=str),
            OpenApiParameter(name='rating',location=OpenApiParameter.QUERY, description='1=asc,0=default,-1=des', required=False, type=str),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        query_set = super().get_queryset()
        price_ordering = self.request.query_params.get("price", "0")
        rating_ordering = self.request.query_params.get("rating", "0")
        order_price = None
        order_rating = None
        price_ordering = int(price_ordering)
        rating_ordering = int(rating_ordering)

        if price_ordering == 1:
            order_price = 'price'
        elif price_ordering == -1:
            order_price = '-price'
        
        if rating_ordering == 1:
            order_rating = 'rating'
        elif rating_ordering == -1:
            order_rating = '-rating'
        
        order_fields = [field for field in [order_price, order_rating] if field is not None]
        if order_fields:
            query_set = query_set.order_by(*order_fields)
        
        return query_set


    def get_serializer_class(self):
        if(self.action == 'retrieve'):
            return serializers.ProductDetailSerializer
        return self.serializer_class
    
    # def get_queryset(self):
    #     return self.queryset.order_by("-p_id")