"""
URL mappings for discount API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from discount import views


router = DefaultRouter()
router.register('discount', views.DiscountCouponViewSet)

app_name = 'discount' #name for reverse url

urlpatterns = [
    path('',include(router.urls)),
]