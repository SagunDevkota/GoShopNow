"""
URL mappings for product API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from product import views


router = DefaultRouter()
router.register('product', views.ProductViewSet)
router.register('cart', views.CartViewSet)
router.register('review',views.ReviewViewSet)

app_name = 'product' #name for reverse url

urlpatterns = [
    path('',include(router.urls)),
]