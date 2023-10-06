"""View for product model"""
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.openapi import OpenApiParameter
from drf_spectacular.utils import extend_schema
from elasticsearch_dsl import Search
from django_elasticsearch_dsl_drf.viewsets import DocumentViewSet
from django_elasticsearch_dsl_drf.filter_backends import CompoundSearchFilterBackend,FilteringFilterBackend

from product import serializers
from core.pagination import CustomPagination
from core.models import Product,Category
from core.documents import ProductDocument
from elasticsearch import exceptions
    
class ProductViewSet(
    DocumentViewSet
    ):
    document = ProductDocument
    serializer_class = serializers.ProductDocumentSerializer
    queryset = Product.objects.order_by('-p_id')
    pagination_class = CustomPagination
    filter_backends = [FilteringFilterBackend,  CompoundSearchFilterBackend]

    search_fields = ['name']

    multi_match_search_fields = ['name']

    filter_fields = {"category":"category"}

    http_method_names = ['get']
    
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
            query_set = query_set.sort(*order_fields)
        return query_set
    
    @extend_schema(
        parameters=[
            OpenApiParameter(name='price',location=OpenApiParameter.QUERY, description='1=asc,0=default,-1=des', required=False, type=str),
            OpenApiParameter(name='rating',location=OpenApiParameter.QUERY, description='1=asc,0=default,-1=des', required=False, type=str),
            OpenApiParameter(name='search',location=OpenApiParameter.QUERY, description='Search Query', required=False, type=str),
            OpenApiParameter(name='category',location=OpenApiParameter.QUERY, description='Category', required=False, type=str),
        ],
    )
    @method_decorator(cache_page(60))
    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            print(e)
            return Response({"error":"Elasticsearch connection failed"},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
        
    @method_decorator(cache_page(60))
    def retrieve(self, request, *args, **kwargs):
        instance = self.queryset.get(p_id=kwargs['pk'])
        serializer = self.get_serializer_class()
        data = serializer(instance).data
        return Response(data)

    def get_serializer_class(self):
        if(self.action == 'retrieve'):
            return serializers.ProductDetailSerializer
        return self.serializer_class
