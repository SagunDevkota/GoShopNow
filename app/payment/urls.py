"""
URL mappings for product API.
"""

from django.urls import path,include

from rest_framework.routers import DefaultRouter

from payment import views


router = DefaultRouter()
router.register('payment', views.PaymentViewSet)

app_name = 'payment' #name for reverse url

urlpatterns = [
    path('',include(router.urls)),
    path('validate/', views.PaymentViewSet.as_view({'get': 'validate'}), name='validate'),
    path('download/',views.PaymentViewSet.as_view({'get':'download'}), name='download')
]