"""
URL mappings for product API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from product import views


router = DefaultRouter()
router.register('product', views.ProductViewSet)

app_name = 'product' #name for reverse url

urlpatterns = [
    path('product/', views.ProductViewSet.as_view({'get': 'list'}), name='product-list'),
    path('product/<int:pk>/', views.ProductViewSet.as_view({'get': 'retrieve'}), name='product-detail'),
]