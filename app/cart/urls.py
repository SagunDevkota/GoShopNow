"""
URL mappings for product API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from cart import views


router = DefaultRouter()
router.register('cart', views.CartViewSet)

app_name = 'cart' #name for reverse url

urlpatterns = [
    path('',include(router.urls)),
]