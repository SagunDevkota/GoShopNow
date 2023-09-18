"""
URL mappings for address API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from address import views


router = DefaultRouter()
router.register('address', views.AddressViewSet)
router.register('delivery-address', views.DeliveryAddressViewSet)

app_name = 'address' #name for reverse url

urlpatterns = [
    path('',include(router.urls)),
]